from app.core.db import db
from app.models import ElectricityBill, ElectricityMeter, MonthlyBill, WaterBill


def test_electricity_water_reports_and_maintenance(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-SMOKE-001",
            "room_number": "A01",
            "notes": "smoke meter",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-SMOKE-001").first()
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
            "prev_reading": "100",
            "curr_reading": "150",
            "total_amount": "500",
            "public_amount": "100",
            "flow_amount": "0",
            "notes": "smoke bill",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        bill = ElectricityBill.query.first()
        electricity_bill_id = bill.id

    response = client.post(
        f"/electricity/bills/{electricity_bill_id}/readings/create",
        data={
            "meter_id": meter_id,
            "room_id": seeded_data["room_id"],
            "prev_reading": "100",
            "curr_reading": "150",
            "calculated_amount": "500",
            "confirmed_amount": "480",
            "notes": "smoke reading",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(f"/electricity/bills/{electricity_bill_id}/calculate", follow_redirects=True)
    assert response.status_code == 200
    response = client.get(f"/electricity/bills/{electricity_bill_id}")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "已計算" in text or "calculated" in text

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
            "actual_usage_1": "10",
            "notes": "smoke water",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        water_bill = WaterBill.query.first()
        water_bill_id = water_bill.id

    response = client.post(
        f"/water/{water_bill_id}/post",
        data={
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "mode": "shared_by_stay_days",
            "amount": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post("/reports/monthly", data={"year_month": "2026-06"}, follow_redirects=True)
    assert response.status_code == 200
    assert "Tenant One" in response.get_data(as_text=True)

    response = client.get("/maintenance/")
    assert response.status_code == 200
    assert "schema" in response.get_data(as_text=True)

    with app.app_context():
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert monthly_bill.water_amount > 0
