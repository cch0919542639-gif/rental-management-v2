from app.core.db import db
from app.models import MonthlyBill, PaymentRecord


def test_billing_monthly_view_and_payment_linking(app, logged_in_client, seeded_data):
    client = logged_in_client
    year_month = "2026-06"

    # Billing page renders for the month
    response = client.get(f"/billing/?year_month={year_month}")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert year_month in text

    # Create a payment for the seeded monthly bill
    response = client.post(
        "/payments/create",
        data={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "12700",
            "transaction_date": "2026-06-20",
            "payer_name": "Tenant One",
            "transaction_id": "TXN-BILL-001",
            "bank_name": "Test Bank",
            "account_number": "12345",
            "account_holder": "Owner A",
            "status_text": "received",
            "ocr_engine": "manual",
            "notes": "integration billing->payments",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        record = PaymentRecord.query.filter_by(transaction_id="TXN-BILL-001").first()
        assert record is not None
        payment_id = record.id

    # Verify payment
    response = client.post(
        f"/payments/{payment_id}/verify",
        data={"notes": "verified"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Link payment to monthly bill (this should mark paid)
    response = client.post(
        f"/payments/{payment_id}/link",
        data={"monthly_bill_id": seeded_data["monthly_bill_id"], "notes": "linked"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert bill is not None
        assert bill.paid is True

    # Billing page renders again for the month (paid-state keyword may be localized)
    response = client.get(f"/billing/?year_month={year_month}")
    assert response.status_code == 200


