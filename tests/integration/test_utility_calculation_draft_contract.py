from datetime import date
from decimal import Decimal

import pytest

from app.core.db import db
from app.core.errors import DomainValidationError
from app.models.billing import MonthlyBill, UtilityCalculationDraft, WaterBill
from app.models.electricity import ElectricityBill, ElectricityMeter, ElectricityReading
from app.services import ElectricityService, WaterService
from app.services.utility_draft_service import UtilityDraftService


def _water_bill(property_id, total_amount):
    bill = WaterBill(
        property_id=property_id,
        billing_start=date(2026, 7, 14),
        billing_end=date(2026, 9, 11),
        total_amount=total_amount,
    )
    db.session.add(bill)
    db.session.flush()
    return bill


def test_water_draft_records_per_room_ceiling_reconciliation(app, seeded_data):
    with app.app_context():
        water_bill = _water_bill(seeded_data["property_id"], 2895)
        draft = UtilityDraftService.create_draft(
            utility_type="water",
            property_id=seeded_data["property_id"],
            year_month="2026-09",
            billing_start="2026-07-14",
            billing_end="2026-09-11",
            billed_total=2895,
            policy_code="water_bill_by_stay_days",
            rounding_mode=UtilityDraftService.PER_ROOM_CEILING,
            water_bill_id=water_bill.id,
        )
        UtilityDraftService.replace_lines(
            draft,
            [
                {
                    "room_number_snapshot": "1",
                    "occupancy_status": "occupied",
                    "stay_days": 60,
                    "calculated_amount": 414,
                },
                {
                    "room_number_snapshot": "7",
                    "occupancy_status": "vacant",
                    "stay_days": 0,
                    "calculated_amount": 0,
                    "exclusion_reason": "空房",
                },
            ],
        )

        assert draft.year_month == "202609"
        assert draft.status == UtilityCalculationDraft.DRAFT
        assert draft.billed_total == Decimal("2895")
        assert draft.allocated_total == Decimal("414")
        assert draft.reconciliation_difference == Decimal("-2481")
        assert draft.lines[1].exclusion_reason == "空房"


def test_draft_must_be_confirmed_before_posting(app, seeded_data):
    with app.app_context():
        water_bill = _water_bill(seeded_data["property_id"], 1191)
        draft = UtilityDraftService.create_draft(
            utility_type="water",
            property_id=seeded_data["property_id"],
            year_month="202609",
            billing_start="2026-07-14",
            billing_end="2026-09-11",
            billed_total=1191,
            policy_code="water_bill_by_stay_days",
            rounding_mode=UtilityDraftService.PER_ROOM_CEILING,
            water_bill_id=water_bill.id,
        )

        with pytest.raises(DomainValidationError, match="確認"):
            UtilityDraftService.mark_posted(draft)

        UtilityDraftService.confirm(draft)
        UtilityDraftService.mark_posted(draft)

        assert draft.status == UtilityCalculationDraft.POSTED


def test_draft_rejects_invalid_room_status_and_late_line_changes(app, seeded_data):
    with app.app_context():
        water_bill = _water_bill(seeded_data["property_id"], 996)
        draft = UtilityDraftService.create_draft(
            utility_type="water",
            property_id=seeded_data["property_id"],
            year_month="202609",
            billing_start="2026-07-14",
            billing_end="2026-09-11",
            billed_total=996,
            policy_code="water_bill_by_stay_days",
            rounding_mode=UtilityDraftService.PER_ROOM_CEILING,
            water_bill_id=water_bill.id,
        )

        with pytest.raises(DomainValidationError, match="房間狀態"):
            UtilityDraftService.replace_lines(
                draft,
                [{"room_number_snapshot": "2", "occupancy_status": "unknown", "stay_days": 0, "calculated_amount": 0}],
            )

        UtilityDraftService.confirm(draft)
        with pytest.raises(DomainValidationError, match="草稿"):
            UtilityDraftService.replace_lines(
                draft,
                [{"room_number_snapshot": "7", "occupancy_status": "vacant", "stay_days": 0, "calculated_amount": 0}],
            )


def test_draft_rejects_source_bill_property_period_or_total_mismatch(app, seeded_data):
    with app.app_context():
        water_bill = _water_bill(seeded_data["property_id"], 996)

        for overrides, message in (
            ({"property_id": seeded_data["property_id"] + 1}, "物件"),
            ({"billing_end": "2026-09-12"}, "帳期"),
            ({"billed_total": 997}, "總額"),
        ):
            payload = {
                "utility_type": "water",
                "property_id": seeded_data["property_id"],
                "year_month": "202609",
                "billing_start": "2026-07-14",
                "billing_end": "2026-09-11",
                "billed_total": 996,
                "policy_code": "water_bill_by_stay_days",
                "rounding_mode": UtilityDraftService.PER_ROOM_CEILING,
                "water_bill_id": water_bill.id,
            }
            payload.update(overrides)

            with pytest.raises(DomainValidationError, match=message):
                UtilityDraftService.create_draft(**payload)


def test_draft_requires_exactly_one_matching_source_bill(app, seeded_data):
    with app.app_context():
        water_bill = _water_bill(seeded_data["property_id"], 996)

        with pytest.raises(DomainValidationError, match="且只能"):
            UtilityDraftService.create_draft(
                utility_type="water",
                property_id=seeded_data["property_id"],
                year_month="202609",
                billing_start="2026-07-14",
                billing_end="2026-09-11",
                billed_total=996,
                policy_code="water_bill_by_stay_days",
                rounding_mode=UtilityDraftService.PER_ROOM_CEILING,
                water_bill_id=water_bill.id,
                electricity_bill_id=1,
            )


def test_water_posting_requires_confirmed_draft_and_preserves_monthly_bill(app, seeded_data):
    with app.app_context():
        water_bill = _water_bill(seeded_data["property_id"], 996)
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        before = monthly_bill.water_amount

        with pytest.raises(DomainValidationError, match="已確認水電草稿"):
            WaterService.post_shared_to_monthly_bill(
                monthly_bill_id=monthly_bill.id,
                water_bill=water_bill,
            )

        assert db.session.get(MonthlyBill, monthly_bill.id).water_amount == before


def test_electricity_posting_requires_confirmed_draft_and_preserves_monthly_bill(app, seeded_data):
    with app.app_context():
        meter = ElectricityMeter(
            property_id=seeded_data["property_id"],
            room_id=seeded_data["room_id"],
            meter_number="A01-TEST",
        )
        db.session.add(meter)
        db.session.flush()
        bill = ElectricityBill(
            property_id=seeded_data["property_id"],
            year_month="202606",
            period_start=date(2026, 6, 1),
            period_end=date(2026, 6, 30),
            total_amount=5,
        )
        db.session.add(bill)
        db.session.flush()
        reading = ElectricityReading(
            bill_id=bill.id,
            meter_id=meter.id,
            room_id=seeded_data["room_id"],
            prev_reading=0,
            curr_reading=1,
            usage=1,
            calculated_amount=5,
        )
        db.session.add(reading)
        db.session.commit()

        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        before = monthly_bill.electricity_amount
        with pytest.raises(DomainValidationError, match="已確認水電草稿"):
            ElectricityService.post_reading_to_monthly_bill(
                monthly_bill_id=monthly_bill.id,
                reading=reading,
            )

        assert db.session.get(MonthlyBill, monthly_bill.id).electricity_amount == before
