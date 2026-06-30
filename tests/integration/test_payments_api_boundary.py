import json

from app.core.db import db
from app.models import PaymentRecord


def test_payment_records_api_create_list_and_detail(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/api/payment-records/",
        json={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "12345",
            "transaction_date": "2026-06-22",
            "payer_name": "Tenant One",
            "transaction_id": "TXN-API-001",
            "bank_name": "API Bank",
            "account_number": "54321",
            "account_holder": "Owner A",
            "status_text": "received",
            "ocr_engine": "boundary",
            "raw_ocr_text": "ocr payload",
            "notes": "api create test",
        },
    )
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["transaction_id"] == "TXN-API-001"
    assert payload["record_status"] == "pending"
    payment_id = payload["id"]

    response = client.get("/api/payment-records/?record_status=pending&limit=10&payer_name=Tenant")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] >= 1
    assert any(item["transaction_id"] == "TXN-API-001" for item in payload["items"])

    response = client.get(f"/api/payment-records/{payment_id}")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == payment_id
    assert payload["amount"] == "12345.00"


def test_payment_records_api_duplicate_transaction_id_returns_conflict(app, logged_in_client, seeded_data):
    client = logged_in_client

    first = client.post(
        "/api/payment-records/",
        json={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "5000",
            "transaction_date": "2026-06-23",
            "payer_name": "Tenant One",
            "transaction_id": "TXN-API-DUP-001",
        },
    )
    assert first.status_code == 201

    second = client.post(
        "/api/payment-records/",
        json={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "5000",
            "transaction_date": "2026-06-23",
            "payer_name": "Tenant One",
            "transaction_id": "TXN-API-DUP-001",
        },
    )
    assert second.status_code == 409
    payload = second.get_json()
    assert payload["error"] == "conflict"


def test_payment_records_api_returns_422_field_details(logged_in_client):
    client = logged_in_client
    response = client.post(
        "/api/payment-records/",
        json={
            "amount": "bad-number",
            "transaction_date": "2026/06/20",
        },
    )
    assert response.status_code == 422
    payload = response.get_json()
    assert payload["error"] == "validation_error"
    assert "details" in payload
    assert "amount" in payload["details"] or "transaction_date" in payload["details"]


def test_payment_records_api_analyze_uses_stored_raw_text(app, logged_in_client, seeded_data):
    client = logged_in_client
    with app.app_context():
        record = PaymentRecord(
            contract_id=seeded_data["contract_id"],
            monthly_bill_id=seeded_data["monthly_bill_id"],
            amount=12000,
            payer_name="Tenant One",
            transaction_id="TXN-OCR-API-001",
            raw_ocr_text="Tenant One 2026-06-20 TXN-OCR-API-001 amount 12000",
            record_status="pending",
        )
        db.session.add(record)
        db.session.commit()
        payment_id = record.id

    response = client.post(f"/api/payment-records/{payment_id}/analyze")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["analysis"]["status"] == "ok"
    assert payload["analysis"]["manual_review_required"] is True
    assert payload["analysis"]["auto_apply"] is False
    assert payload["analysis"]["extracted_candidates"]["transaction_id"] == "TXN-OCR-API-001"

    with app.app_context():
        record = db.session.get(PaymentRecord, payment_id)
        assert record.record_status == "pending"
        stored = json.loads(record.raw_llm_response)
        assert stored["manual_review_required"] is True


def test_payment_records_api_analyze_gracefully_handles_missing_provider(app, logged_in_client, seeded_data):
    client = logged_in_client
    with app.app_context():
        record = PaymentRecord(
            contract_id=seeded_data["contract_id"],
            monthly_bill_id=seeded_data["monthly_bill_id"],
            amount=12000,
            payer_name="Tenant One",
            transaction_id="TXN-OCR-API-002",
            image_path="receipt.jpg",
            record_status="pending",
        )
        db.session.add(record)
        db.session.commit()
        payment_id = record.id

    response = client.post(f"/api/payment-records/{payment_id}/analyze")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["analysis"]["status"] == "not_configured"
    assert payload["analysis"]["provider"] == "noop"
