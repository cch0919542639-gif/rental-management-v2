from datetime import date
from decimal import Decimal

from app.core.db import db
from app.models import Contract, ElectricityBill, ElectricityMeter, ElectricityReading, Room, Tenant
from app.services import ElectricityService


def test_property_preview_allocates_usage_and_public_electricity_without_posting(app, seeded_data):
    with app.app_context():
        prop_id = seeded_data["property_id"]
        property_row = db.session.get(Room, seeded_data["room_id"]).property
        property_row.electricity_policy_code = "electricity_bill_usage_ratio_plus_public_share"
        room_two = Room(property_id=prop_id, room_number="A02", status="occupied")
        vacant = Room(property_id=prop_id, room_number="A03", status="vacant")
        tenant = Tenant(name="Tenant Two")
        db.session.add_all([room_two, vacant, tenant])
        db.session.flush()
        db.session.add(Contract(tenant_id=tenant.id, room_id=room_two.id, start_date=date(2026, 1, 1), end_date=date(2026, 7, 31), rent=Decimal("10000"), deposit=Decimal("20000"), status="active"))
        meter_one = ElectricityMeter(property_id=prop_id, room_id=seeded_data["room_id"], meter_number="A01-M")
        meter_two = ElectricityMeter(property_id=prop_id, room_id=room_two.id, meter_number="A02-M")
        db.session.add_all([meter_one, meter_two])
        db.session.flush()
        bill = ElectricityBill(property_id=prop_id, period_start=date(2026, 8, 1), period_end=date(2026, 8, 31), year_month="202609", prev_reading=0, curr_reading=0, total_amount=Decimal("1000"), public_amount=Decimal("200"))
        db.session.add(bill)
        db.session.flush()
        db.session.add_all([
            ElectricityReading(bill_id=bill.id, meter_id=meter_one.id, room_id=seeded_data["room_id"], prev_reading=10, curr_reading=110, usage=100),
            ElectricityReading(bill_id=bill.id, meter_id=meter_two.id, room_id=room_two.id, prev_reading=20, curr_reading=320, usage=300),
        ])
        db.session.commit()

        preview = ElectricityService.preview_property_bill(bill=bill)

        assert preview["blockers"] == []
        assert preview["can_create_draft"] is True
        assert preview["allocated_total"] == Decimal("1000.00")
        assert preview["unallocated_difference"] == Decimal("0.00")
        by_room = {row["room_number"]: row for row in preview["rows"]}
        assert by_room["A01"]["allocated_amount"] == Decimal("300.00")
        assert by_room["A02"]["allocated_amount"] == Decimal("700.00")
        assert by_room["A03"]["reason"] == "空房未抄表"


def test_property_preview_blocks_mismatched_meter_and_negative_reading(app, seeded_data):
    with app.app_context():
        prop_id = seeded_data["property_id"]
        meter = ElectricityMeter(property_id=prop_id, room_id=seeded_data["room_id"], meter_number="A01-M")
        db.session.add(meter)
        db.session.flush()
        bill = ElectricityBill(property_id=prop_id, period_start=date(2026, 8, 1), period_end=date(2026, 8, 31), year_month="202609", total_amount=Decimal("100"))
        db.session.add(bill)
        db.session.flush()
        db.session.add(ElectricityReading(bill_id=bill.id, meter_id=meter.id, room_id=seeded_data["room_id"], prev_reading=200, curr_reading=100, usage=-100))
        db.session.commit()

        preview = ElectricityService.preview_property_bill(bill=bill)

        assert preview["can_create_draft"] is False
        assert any("讀數倒退" in blocker for blocker in preview["blockers"])
