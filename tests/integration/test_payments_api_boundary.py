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

    response = client.get("/api/payment-records/?record_status=pending&limit=10")
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
