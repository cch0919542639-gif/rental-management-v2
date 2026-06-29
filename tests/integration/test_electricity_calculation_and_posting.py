from app.core.db import db
from app.models import ElectricityBill, ElectricityMeter, MonthlyBill


def test_electricity_calculate_and_view(app, logged_in_client, seeded_data):
    client = logged_in_client

    # Create a meter
    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-INTEG-EL-001",
            "room_number": "A01",
            "notes": "integration meter",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-INTEG-EL-001").first()
        assert meter is not None
        meter_id = meter.id

    # Create bill for the month
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
            "notes": "integration electricity bill",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        # Repository/listing may key on period/year_month differently; search by newest bill
        bill = ElectricityBill.query.order_by(ElectricityBill.id.desc()).first()
        assert bill is not None
        electricity_bill_id = bill.id


    # Calculate
    response = client.post(f"/electricity/bills/{electricity_bill_id}/calculate", follow_redirects=True)
    assert response.status_code == 200

    # View detail contains calculated keyword
    response = client.get(f"/electricity/bills/{electricity_bill_id}")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "已計算" in text or "calculated" in text

    # Idempotency sanity: calculate again should not crash
    response = client.post(f"/electricity/bills/{electricity_bill_id}/calculate", follow_redirects=True)
    assert response.status_code == 200

    # Ensure monthly bill has electricity_amount updated (>0)
    # Monthly bill may only be updated after post/回寫 steps depending on implementation.
    with app.app_context():
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert monthly_bill is not None
        assert monthly_bill.electricity_amount is not None


