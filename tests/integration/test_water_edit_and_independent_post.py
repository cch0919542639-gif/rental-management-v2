"""
test_water_edit_and_independent_post.py

Phase 2 — Water: edit flow, independent mode posting, reports coverage.

Covers:
  1. Create a water bill -> edit it -> verify update
  2. Post water bill with independent mode -> verify monthly_bill.water_amount
  3. Reports: landlord summary and yearly overview render 200
  4. Placeholder: shared_by_stay_days multi-contract allocation (skip)

Constraints:
  - Does NOT modify WaterService or WaterBill model.
  - Does NOT alter water allocation rules.
"""

import pytest
from app.core.db import db
from app.models import MonthlyBill, WaterBill


def test_water_bill_edit(app, logged_in_client, seeded_data):
    """Create a water bill, edit its total_amount, verify the update."""
    client = logged_in_client

    response = client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-06-01",
            "billing_end": "2026-06-30",
            "total_amount": "500",
            "meter_prev_1": "100",
            "meter_curr_1": "150",
            "sub_meter_1": "50",
            "actual_usage_1": "50",
            "notes": "initial edit test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        water_bill = WaterBill.query.filter_by(total_amount=500).first()
        assert water_bill is not None
        water_bill_id = water_bill.id
        assert water_bill.notes == "initial edit test"

    # Edit water bill
    response = client.post(
        f"/water/{water_bill_id}/edit",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-06-01",
            "billing_end": "2026-06-30",
            "total_amount": "600",
            "meter_prev_1": "100",
            "meter_curr_1": "150",
            "sub_meter_1": "50",
            "actual_usage_1": "50",
            "notes": "updated edit test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        water_bill = db.session.get(WaterBill, water_bill_id)
        assert water_bill.total_amount == 600
        assert water_bill.notes == "updated edit test"


def test_water_independent_post(app, logged_in_client, seeded_data):
    """Create a water bill -> post with independent mode -> verify monthly bill."""
    client = logged_in_client

    # Create water bill
    response = client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-06-01",
            "billing_end": "2026-06-30",
            "total_amount": "350",
            "meter_prev_1": "50",
            "meter_curr_1": "80",
            "sub_meter_1": "30",
            "actual_usage_1": "30",
            "notes": "independent post test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        water_bill = WaterBill.query.filter_by(total_amount=350).first()
        assert water_bill is not None
        water_bill_id = water_bill.id

    # Post with independent mode
    response = client.post(
        f"/water/{water_bill_id}/post",
        data={
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "mode": "independent_meter",
            "amount": "350",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert monthly_bill.water_amount == 350, (
            f"Expected water_amount=350, got {monthly_bill.water_amount}"
        )


def test_reports_landlord_summary(app, logged_in_client, seeded_data):
    """Reports landlord-summary page should render."""
    client = logged_in_client

    response = client.post(
        "/reports/landlord-summary",
        data={"year_month": "2026-06"},
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_reports_yearly_overview(app, logged_in_client, seeded_data):
    """Reports yearly-overview page should render."""
    client = logged_in_client

    response = client.post(
        "/reports/yearly",
        data={"year": "2026"},
        follow_redirects=True,
    )
    assert response.status_code == 200


@pytest.mark.skip(reason="Placeholder: shared_by_stay_days water allocation with "
                         "multiple active contracts in the same property. Will "
                         "verify proportional split when 2+ tenants share a water meter.")
def test_water_shared_multi_contract():
    """Placeholder — shared water allocation across 2+ contracts (TBD)."""
    ...
