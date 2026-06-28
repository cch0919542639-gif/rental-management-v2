from decimal import Decimal

from app.core.db import db
from app.models import ElectricityBill, ElectricityMeter, ElectricityReading, MonthlyBill, WaterBill


def test_electricity_rate_fallback_and_bill_aggregation(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-ALG-001",
            "room_number": "A01",
            "notes": "algorithm meter",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-ALG-001").first()
        meter_id = meter.id

    response = client.post(
        "/electricity/bills/create",
        data={
            "property_id": seeded_data["property_id"],
            "meter_id": meter_id,
            "calc_method_id": seeded_data["calc_method_id"],
            "year_month": "2026-06",
            "period_start": "2026-06-01",
            "period_end": "2026-06-30",
            "prev_reading": "0",
            "curr_reading": "100",
            "total_amount": "0",
            "public_amount": "50",
            "flow_amount": "0",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        bill = ElectricityBill.query.order_by(ElectricityBill.id.desc()).first()
        bill_id = bill.id

    response = client.post(
        f"/electricity/bills/{bill_id}/readings/create",
        data={
            "meter_id": meter_id,
            "room_id": seeded_data["room_id"],
            "prev_reading": "10",
            "curr_reading": "20",
            "notes": "no manual calculated_amount",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(f"/electricity/bills/{bill_id}/calculate", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        reading = ElectricityReading.query.filter_by(bill_id=bill_id).first()
        bill = db.session.get(ElectricityBill, bill_id)
        assert reading.calculated_amount == Decimal("50.00")
        assert bill.flow_amount == Decimal("50.00")
        assert bill.total_amount == Decimal("100.00")
        assert bill.total_usage == Decimal("10.0")


def test_water_shared_post_updates_usage_proportionally(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-06-01",
            "billing_end": "2026-06-30",
            "total_amount": "300",
            "meter_prev_1": "10",
            "meter_curr_1": "20",
            "sub_meter_1": "10",
            "actual_usage_1": "12",
            "meter_prev_2": "0",
            "meter_curr_2": "0",
            "sub_meter_2": "0",
            "actual_usage_2": "3",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        water_bill = WaterBill.query.order_by(WaterBill.id.desc()).first()
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert water_bill is not None
        water_bill_id = water_bill.id
        assert monthly_bill is not None

    response = client.post(
        f"/water/{water_bill_id}/post",
        data={
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "mode": "shared_by_stay_days",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert monthly_bill.water_amount == Decimal("300.00")
        assert monthly_bill.water_usage == Decimal("15.0")
