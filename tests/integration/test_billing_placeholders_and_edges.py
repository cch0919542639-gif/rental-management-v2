"""
test_billing_placeholders_and_edges.py

Phase 2 — Billing edge cases + placeholder for deeper billing algorithm tests.

Covers:
  1. Billing list renders for a month with no bills (should return 200)
  2. Billing list with default month (no ?month= param)
  3. Placeholder: deeper billing calculation tests (skipped)

Constraints:
  - Does NOT modify core billing logic or data contracts.
  - Does NOT alter MonthlyBill model or its relationships.
"""

import pytest


def test_billing_list_without_bills_for_month(app, logged_in_client, seeded_data):
    """Billing page should render 200 even when no bills exist for a specific month."""
    client = logged_in_client

    # Use a month that is unlikely to have data (future month)
    response = client.get("/billing/?year_month=2099-12")
    assert response.status_code == 200


def test_billing_list_default_month(app, logged_in_client, seeded_data):
    """Billing page renders with the default month (no query param)."""
    client = logged_in_client

    response = client.get("/billing/")
    assert response.status_code == 200


@pytest.mark.skip(reason="Placeholder: deeper billing recalculation test not yet written. "
                         "This will test the billing recalculation endpoint/service "
                         "once deeper billing algorithm is implemented in Phase 3.")
def test_billing_recalculate():
    """Placeholder — billing recalculation logic (TBD)."""
    ...


@pytest.mark.skip(reason="Placeholder: billing summarisation / aggregation test. "
                         "Will verify month_collected and month_unpaid totals "
                         "after multiple payments are linked.")
def test_billing_summary_consistency():
    """Placeholder — billing summary consistency (TBD)."""
    ...
