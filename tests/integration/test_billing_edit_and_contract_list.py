"""
test_billing_edit_and_contract_list.py

Phase 2 Round 2 — Billing edit flow and contract-specific billing list page.

Covers:
  1. Edit an existing monthly bill (change other_charges, verify total recalculated)
  2. GET /billing/contracts/<id>/ renders 200
  3. Placeholder: billing edit with conflict (skip)
"""

import pytest
from app.core.db import db
from app.models import MonthlyBill


def test_billing_edit_updates_total(app, logged_in_client, seeded_data):
    """Edit a monthly bill's other_charges, verify total is recalculated."""
    client = logged_in_client
    bill_id = seeded_data["monthly_bill_id"]

    response = client.get(f"/billing/{bill_id}/edit")
    assert response.status_code == 200

    response = client.post(
        f"/billing/{bill_id}/edit",
        data={
            "contract_id": seeded_data["contract_id"],
            "year_month": "2026-06",
            "rent": "12000",
            "electricity_prev": "0",
            "electricity_curr": "0",
            "electricity_usage": "0",
            "electricity_amount": "0",
            "public_electricity": "0",
            "water_prev": "0",
            "water_curr": "0",
            "water_usage": "0",
            "water_amount": "0",
            "other_charges": "200",
            "other_desc": "test fee",
            "paid": "y",
            "notes": "edit test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        bill = db.session.get(MonthlyBill, bill_id)
        assert float(bill.other_charges) == 200.0
        assert float(bill.total) == 12200.0  # 12000 rent + 200 other = 12200
        assert bill.paid is True


def test_billing_contract_list_renders(app, logged_in_client, seeded_data):
    """The contract-specific billing list page should render 200."""
    client = logged_in_client
    response = client.get(f"/billing/contracts/{seeded_data['contract_id']}")
    assert response.status_code == 200


@pytest.mark.skip(reason="Placeholder: billing edit with conflict detection (TBD).")
def test_billing_edit_conflict():
    ...


@pytest.mark.skip(reason="Placeholder: toggle-paid idempotency (TBD).")
def test_billing_toggle_paid_idempotency():
    ...
