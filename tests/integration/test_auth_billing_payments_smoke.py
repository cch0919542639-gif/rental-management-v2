from app.core.db import db
from app.models import MonthlyBill, PaymentRecord


def test_auth_dashboard_and_payment_flow(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.get("/")
    assert response.status_code == 200
    assert "Dashboard" in response.get_data(as_text=True)

    response = client.get("/billing/?year_month=2026-06")
    assert response.status_code == 200
    assert "2026-06" in response.get_data(as_text=True)

    response = client.post(
        "/payments/create",
        data={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "12700",
            "transaction_date": "2026-06-20",
            "payer_name": "Tenant One",
            "transaction_id": "TXN-SMOKE-001",
            "bank_name": "Test Bank",
            "account_number": "12345",
            "account_holder": "Owner A",
            "status_text": "received",
            "ocr_engine": "manual",
            "notes": "smoke",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        record = PaymentRecord.query.filter_by(transaction_id="TXN-SMOKE-001").first()
        assert record is not None
        payment_id = record.id

    response = client.post(f"/payments/{payment_id}/verify", data={"notes": "verified"}, follow_redirects=True)
    assert response.status_code == 200

    response = client.post(
        f"/payments/{payment_id}/link",
        data={"monthly_bill_id": seeded_data["monthly_bill_id"], "notes": "linked"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        record = db.session.get(PaymentRecord, payment_id)
        bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert record.record_status == "linked"
        assert bill.paid is True
