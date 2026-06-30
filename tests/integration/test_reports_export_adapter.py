from io import BytesIO

from openpyxl import load_workbook

from app.models import PaymentRecord


def _seed_paid_bill(app, client, seeded_data, transaction_id: str):
    response = client.post(
        "/payments/create",
        data={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "12700",
            "transaction_date": "2026-06-20",
            "payer_name": "Tenant One",
            "transaction_id": transaction_id,
            "bank_name": "Test Bank",
            "account_number": "12345",
            "account_holder": "Owner A",
            "status_text": "received",
            "ocr_engine": "manual",
            "notes": "export integration",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        record = PaymentRecord.query.filter_by(transaction_id=transaction_id).first()
        payment_id = record.id
    assert client.post(f"/payments/{payment_id}/verify", data={"notes": "verified"}, follow_redirects=True).status_code == 200
    assert (
        client.post(
            f"/payments/{payment_id}/link",
            data={"monthly_bill_id": seeded_data["monthly_bill_id"], "notes": "linked"},
            follow_redirects=True,
        ).status_code
        == 200
    )


def test_monthly_report_export_csv(app, logged_in_client, seeded_data):
    client = logged_in_client
    _seed_paid_bill(app, client, seeded_data, "TXN-EXPORT-001")

    response = client.get("/reports/monthly/export?year_month=2026-06&format=csv")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/csv")
    assert 'monthly-report-2026-06.csv' in response.headers["Content-Disposition"]
    text = response.get_data(as_text=True)
    assert "tenant_name" in text
    assert "Tenant One" in text


def test_landlord_summary_export_xlsx(app, logged_in_client, seeded_data):
    client = logged_in_client
    _seed_paid_bill(app, client, seeded_data, "TXN-EXPORT-002")

    response = client.get("/reports/landlord-summary/export?year_month=2026-06&format=xlsx")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    workbook = load_workbook(BytesIO(response.data))
    sheet = workbook.active
    assert sheet["A1"].value == "landlord_id"
    assert sheet["B2"].value == "Owner A"


def test_report_export_rejects_unknown_format(logged_in_client):
    client = logged_in_client
    response = client.get(
        "/reports/monthly/export?year_month=2026-06&format=pdf",
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 422
    payload = response.get_json()
    assert payload["error"] == "validation_error"
    assert "format" in payload["details"]
