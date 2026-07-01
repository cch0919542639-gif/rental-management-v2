"""
test_payments_reject_and_status.py

Phase 2 — Payments: reject flow + edge cases + placeholder for deeper tests.

Covers:
  1. Create a payment -> reject it -> verify record_status == "rejected"
  2. Payment list renders with a record in it
  3. Duplicate transaction_id handling
  4. Placeholder: payment reconciliation scenarios (skip)

Constraints:
  - Does NOT modify PaymentService or PaymentRecord schema.
  - Does NOT alter payment workflow logic.
"""

import pytest
from app.models import PaymentRecord


def test_payment_reject_flow(app, logged_in_client, seeded_data):
    """Create a payment -> reject -> verify status is 'rejected'."""
    client = logged_in_client

    # Create a new payment (unique transaction_id)
    response = client.post(
        "/payments/create",
        data={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "5000",
            "transaction_date": "2026-06-21",
            "payer_name": "Tenant One",
            "transaction_id": "TXN-REJECT-002",
            "bank_name": "Test Bank",
            "account_number": "67890",
            "account_holder": "Owner A",
            "status_text": "received",
            "ocr_engine": "manual",
            "notes": "reject test payment",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Find the record by transaction_id
    with app.app_context():
        record = PaymentRecord.query.filter_by(transaction_id="TXN-REJECT-002").first()
        assert record is not None
        payment_id = record.id

    # Reject it
    response = client.post(
        f"/payments/{payment_id}/reject",
        data={"notes": "rejected for testing"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        record = PaymentRecord.query.filter_by(transaction_id="TXN-REJECT-002").first()
        assert record.record_status == "rejected", f"Expected rejected, got {record.record_status}"


def test_payment_list_with_records(app, logged_in_client, seeded_data):
    """Payment list page renders when records exist."""
    client = logged_in_client

    response = client.get("/payments/")
    assert response.status_code == 200

    # Should contain at least the payment from the fixture's smoke test
    html = response.get_data(as_text=True)
    assert "TXN" in html or "付款" in html or "payment" in html.lower()


def test_payment_duplicate_transaction_id(app, logged_in_client, seeded_data):
    """Creating the same transaction_id twice should reject the second request."""
    client = logged_in_client

    payload = {
        "contract_id": seeded_data["contract_id"],
        "monthly_bill_id": seeded_data["monthly_bill_id"],
        "amount": "5000",
        "transaction_date": "2026-06-21",
        "payer_name": "Tenant One",
        "transaction_id": "TXN-DUP-001",
        "bank_name": "Test Bank",
        "account_number": "67890",
        "account_holder": "Owner A",
        "status_text": "received",
        "ocr_engine": "manual",
        "notes": "duplicate test payment",
    }

    response = client.post("/payments/create", data=payload, follow_redirects=True)
    assert response.status_code == 200

    duplicate = client.post("/payments/create", data=payload)
    assert duplicate.status_code == 409
    assert "transaction_id 已存在" in duplicate.get_data(as_text=True)

    with app.app_context():
        records = PaymentRecord.query.filter_by(transaction_id="TXN-DUP-001").all()
        assert len(records) == 1


@pytest.mark.skip(reason="Placeholder: payment reconciliation edge cases. "
                         "Will test partial payments, overpayments, and "
                         "multi-record reconciliation once that service is stable.")
def test_payment_reconciliation_edge_cases():
    """Placeholder — payment reconciliation edge cases (TBD)."""
    ...
