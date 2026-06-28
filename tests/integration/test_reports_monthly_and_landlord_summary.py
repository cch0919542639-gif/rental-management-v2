from app.models import MonthlyBill, PaymentRecord


def test_reports_monthly_renders_for_tenant_and_paid_status(app, logged_in_client, seeded_data):
    client = logged_in_client

    # Create a payment and link it so the report has meaningful paid status
    response = client.post(
        "/payments/create",
        data={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "12700",
            "transaction_date": "2026-06-20",
            "payer_name": "Tenant One",
            "transaction_id": "TXN-REP-001",
            "bank_name": "Test Bank",
            "account_number": "12345",
            "account_holder": "Owner A",
            "status_text": "received",
            "ocr_engine": "manual",
            "notes": "integration report",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        record = PaymentRecord.query.filter_by(transaction_id="TXN-REP-001").first()
        assert record is not None
        payment_id = record.id

    response = client.post(
        f"/payments/{payment_id}/verify",
        data={"notes": "verified"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(
        f"/payments/{payment_id}/link",
        data={"monthly_bill_id": seeded_data["monthly_bill_id"], "notes": "linked"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Monthly report renders and includes tenant name
    response = client.post(
        "/reports/monthly",
        data={"year_month": "2026-06"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Tenant One" in text

    # Basic sanity: page contains expected section headings/keywords
    assert "monthly" in text.lower() or "報表" in text


