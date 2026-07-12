from datetime import date
from decimal import Decimal

from app.core.db import db
from app.models import Contract, ElectricityBill, ElectricityMeter, ElectricityReading, MonthlyBill, Room, Tenant, WaterBill
from app.services import ElectricityService, UtilityPolicyResolver


def _create_second_room_contract(app, seeded_data):
    with app.app_context():
        room = Room(
            property_id=seeded_data["property_id"],
            room_number="A02",
            rent=Decimal("10000"),
            deposit=Decimal("20000"),
            status="occupied",
        )
        tenant = Tenant(name="Tenant Two", phone="0922333444")
        db.session.add_all([room, tenant])
        db.session.flush()

        contract = Contract(
            tenant_id=tenant.id,
            room_id=room.id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            rent=Decimal("10000"),
            deposit=Decimal("20000"),
            electricity_rate=Decimal("5"),
            water_rate=Decimal("100"),
            status="active",
        )
        db.session.add(contract)
        db.session.flush()

        monthly_bill = MonthlyBill(
            contract_id=contract.id,
            year_month="202606",
            rent=Decimal("10000"),
            electricity_amount=Decimal("0"),
            public_electricity=Decimal("0"),
            water_amount=Decimal("0"),
            other_charges=Decimal("0"),
            total=Decimal("10000"),
            paid=False,
        )
        db.session.add(monthly_bill)
        db.session.commit()
        return {
            "room_id": room.id,
            "contract_id": contract.id,
            "monthly_bill_id": monthly_bill.id,
        }


def test_electricity_bill_usage_ratio_calculates_and_posts(app, logged_in_client, seeded_data):
    second = _create_second_room_contract(app, seeded_data)

    with app.app_context():
        room = db.session.get(Room, seeded_data["room_id"])
        room.property.electricity_policy_code = UtilityPolicyResolver.BILL_USAGE_RATIO
        meter_a = ElectricityMeter(property_id=seeded_data["property_id"], room_id=seeded_data["room_id"], meter_number="M-B2-001")
        meter_b = ElectricityMeter(property_id=seeded_data["property_id"], room_id=second["room_id"], meter_number="M-B2-002")
        db.session.add_all([meter_a, meter_b])
        db.session.flush()

        bill = ElectricityService.create_bill(
            property_id=seeded_data["property_id"],
            meter_id=meter_a.id,
            calc_method_id=seeded_data["calc_method_id"],
            year_month="2026-06",
            period_start=date(2026, 6, 1),
            period_end=date(2026, 6, 30),
            prev_reading=Decimal("0"),
            curr_reading=Decimal("30"),
            total_amount=Decimal("300"),
            public_amount=Decimal("0"),
            flow_amount=Decimal("0"),
            notes="batch2 ratio",
        )
        ElectricityService.add_reading(
            bill,
            meter_id=meter_a.id,
            room_id=seeded_data["room_id"],
            prev_reading=Decimal("0"),
            curr_reading=Decimal("10"),
        )
        ElectricityService.add_reading(
            bill,
            meter_id=meter_b.id,
            room_id=second["room_id"],
            prev_reading=Decimal("0"),
            curr_reading=Decimal("20"),
        )
        ElectricityService.calculate_bill(bill)
        first_reading = ElectricityReading.query.filter_by(bill_id=bill.id, room_id=seeded_data["room_id"]).first()
        assert first_reading is not None
        ElectricityService.post_reading_to_monthly_bill(
            monthly_bill_id=seeded_data["monthly_bill_id"],
            reading=first_reading,
        )

        readings = ElectricityReading.query.filter_by(bill_id=bill.id).order_by(ElectricityReading.id.asc()).all()
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert readings[0].calculated_amount == Decimal("100.00")
        assert readings[1].calculated_amount == Decimal("200.00")
        assert monthly_bill.electricity_amount == Decimal("100.00")
        assert monthly_bill.public_electricity == Decimal("0.00")


def test_electricity_public_share_policy_splits_public_amount_on_post(app, logged_in_client, seeded_data):
    second = _create_second_room_contract(app, seeded_data)

    with app.app_context():
        room = db.session.get(Room, seeded_data["room_id"])
        room.property.electricity_policy_code = UtilityPolicyResolver.BILL_USAGE_RATIO_PLUS_PUBLIC
        meter_a = ElectricityMeter(property_id=seeded_data["property_id"], room_id=seeded_data["room_id"], meter_number="M-B2-101")
        meter_b = ElectricityMeter(property_id=seeded_data["property_id"], room_id=second["room_id"], meter_number="M-B2-102")
        db.session.add_all([meter_a, meter_b])
        db.session.flush()

        bill = ElectricityService.create_bill(
            property_id=seeded_data["property_id"],
            meter_id=meter_a.id,
            calc_method_id=seeded_data["calc_method_id"],
            year_month="2026-06",
            period_start=date(2026, 6, 1),
            period_end=date(2026, 6, 30),
            prev_reading=Decimal("0"),
            curr_reading=Decimal("30"),
            total_amount=Decimal("360"),
            public_amount=Decimal("60"),
            flow_amount=Decimal("0"),
            notes="batch2 public share",
        )
        ElectricityService.add_reading(
            bill,
            meter_id=meter_a.id,
            room_id=seeded_data["room_id"],
            prev_reading=Decimal("0"),
            curr_reading=Decimal("10"),
        )
        ElectricityService.add_reading(
            bill,
            meter_id=meter_b.id,
            room_id=second["room_id"],
            prev_reading=Decimal("0"),
            curr_reading=Decimal("20"),
        )
        ElectricityService.calculate_bill(bill)

        first_reading = ElectricityReading.query.filter_by(bill_id=bill.id, room_id=seeded_data["room_id"]).first()
        second_reading = ElectricityReading.query.filter_by(bill_id=bill.id, room_id=second["room_id"]).first()
        assert first_reading is not None
        assert second_reading is not None
        ElectricityService.post_reading_to_monthly_bill(
            monthly_bill_id=seeded_data["monthly_bill_id"],
            reading=first_reading,
        )

        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert first_reading.calculated_amount == Decimal("130.00")
        assert second_reading.calculated_amount == Decimal("230.00")
        assert monthly_bill.electricity_amount == Decimal("100.00")
        assert monthly_bill.public_electricity == Decimal("30.00")


def test_water_auto_policy_shared_by_stay_days_preview_and_post(app, logged_in_client, seeded_data):
    client = logged_in_client

    with app.app_context():
        room = db.session.get(Room, seeded_data["room_id"])
        room.property.water_policy_code = UtilityPolicyResolver.WATER_BILL_BY_STAY_DAYS
        db.session.commit()

    client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-06-01",
            "billing_end": "2026-06-30",
            "total_amount": "300",
            "actual_usage_1": "15",
            "notes": "batch2 auto shared",
        },
        follow_redirects=True,
    )

    with app.app_context():
        water_bill = WaterBill.query.filter_by(notes="batch2 auto shared").first()
        assert water_bill is not None

    response = client.post(
        f"/water/{water_bill.id}/preview",
        data={
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "mode": "auto_policy",
            "amount": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "water_bill_by_stay_days" in response.get_data(as_text=True)

    client.post(
        f"/water/{water_bill.id}/post",
        data={
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "mode": "auto_policy",
            "amount": "",
        },
        follow_redirects=True,
    )

    with app.app_context():
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert monthly_bill.water_amount == Decimal("300.00")
        assert monthly_bill.water_usage == Decimal("15.0")


def test_water_auto_policy_free_sets_zero_amount(app, logged_in_client, seeded_data):
    client = logged_in_client

    with app.app_context():
        room = db.session.get(Room, seeded_data["room_id"])
        room.property.water_policy_code = UtilityPolicyResolver.WATER_FREE
        db.session.commit()

    client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-06-01",
            "billing_end": "2026-06-30",
            "total_amount": "300",
            "actual_usage_1": "15",
            "notes": "batch2 auto free",
        },
        follow_redirects=True,
    )

    with app.app_context():
        water_bill = WaterBill.query.filter_by(notes="batch2 auto free").first()
        assert water_bill is not None

    response = client.post(
        f"/water/{water_bill.id}/preview",
        data={
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "mode": "auto_policy",
            "amount": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "water_free" in text
    assert "0" in text

    client.post(
        f"/water/{water_bill.id}/post",
        data={
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "mode": "auto_policy",
            "amount": "",
        },
        follow_redirects=True,
    )

    with app.app_context():
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert monthly_bill.water_amount == Decimal("0.00")
        assert monthly_bill.water_usage == Decimal("0.0")
