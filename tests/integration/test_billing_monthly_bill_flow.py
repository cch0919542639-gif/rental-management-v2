from app.core.db import db
from app.models import MonthlyBill, PaymentRecord
from app.repositories import BillingRepository


def test_billing_monthly_view_and_payment_linking(app, logged_in_client, seeded_data):
    client = logged_in_client
    year_month = "2026-06"

    # Billing page renders for the month.
    response = client.get(f"/billing/?year_month={year_month}")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert year_month in text

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

    assert client.post(f"/payments/{payment_id}/verify", data={"notes": "verified"}, follow_redirects=True).status_code == 200
    assert client.post(
        f"/payments/{payment_id}/link",
        data={"monthly_bill_id": seeded_data["monthly_bill_id"], "notes": "linked"},
        follow_redirects=True,
    ).status_code == 200

    with app.app_context():
        bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert bill is not None
        assert bill.paid is True

    assert client.get(f"/billing/?year_month={year_month}").status_code == 200


def test_multiple_linked_partial_payments_mark_bill_paid(app, logged_in_client, seeded_data):
    client = logged_in_client
    bill_id = seeded_data["monthly_bill_id"]
    contract_id = seeded_data["contract_id"]

    def create_verify_link(amount, transaction_id):
        response = client.post(
            "/payments/create",
            data={
                "contract_id": contract_id,
                "monthly_bill_id": bill_id,
                "amount": str(amount),
                "transaction_date": "2026-06-20",
                "payer_name": "Tenant One",
                "transaction_id": transaction_id,
                "bank_name": "Test Bank",
                "account_number": "12345",
                "account_holder": "Owner A",
                "status_text": "received",
                "ocr_engine": "manual",
                "notes": "partial payment test",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        with app.app_context():
            record = PaymentRecord.query.filter_by(transaction_id=transaction_id).first()
            assert record is not None
            payment_id = record.id
        assert client.post(f"/payments/{payment_id}/verify", data={"notes": "verified"}, follow_redirects=True).status_code == 200
        assert client.post(f"/payments/{payment_id}/link", data={"monthly_bill_id": bill_id, "notes": "linked"}, follow_redirects=True).status_code == 200

    create_verify_link(5000, "TXN-PARTIAL-001")
    with app.app_context():
        assert db.session.get(MonthlyBill, bill_id).paid is False
        assert BillingRepository.prior_unpaid_balance(contract_id, "2026-07") == 7000

    create_verify_link(7000, "TXN-PARTIAL-002")
    with app.app_context():
        assert db.session.get(MonthlyBill, bill_id).paid is True
        assert BillingRepository.prior_unpaid_balance(contract_id, "2026-07") == 0
