"""
test_electricity_water_edge_cases.py

Phase 2 Round 2 — Electricity and water edge cases not covered by existing tests.

Covers:
  1. Water bill with minimum non-zero amount
  2. Water bill with large total_amount (edge case: high value)
  3. Electricity: multi-bill on same meter
  4. Placeholder: reading without calculated_amount (skip)
  5. Placeholder: single-contract shared water allocation (skip)
"""

import pytest
from app.core.db import db
from app.models import ElectricityBill, ElectricityMeter, WaterBill


def test_water_bill_min_amount(app, logged_in_client, seeded_data):
    """Create a water bill with minimum non-zero amount (DataRequired rejects Decimal(0))."""
    client = logged_in_client
    response = client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-07-01",
            "billing_end": "2026-07-15",
            "total_amount": "1",
            "meter_prev_1": "100",
            "meter_curr_1": "100",
            "sub_meter_1": "0",
            "actual_usage_1": "0",
            "notes": "min amount test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        bill = WaterBill.query.filter_by(total_amount=1).first()
        assert bill is not None
        assert float(bill.total_amount) == 1.0


def test_water_bill_large_amount(app, logged_in_client, seeded_data):
    """Create a water bill with a large total_amount."""
    client = logged_in_client
    response = client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-07-01",
            "billing_end": "2026-07-31",
            "total_amount": "99999",
            "meter_prev_1": "0",
            "meter_curr_1": "1000",
            "sub_meter_1": "500",
            "actual_usage_1": "500",
            "notes": "large amount test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        bill = WaterBill.query.filter_by(total_amount=99999).first()
        assert bill is not None
        assert float(bill.total_amount) == 99999.0


def test_electricity_multiple_bills_same_meter(app, logged_in_client, seeded_data):
    """Create a meter, then two bills on the same meter — both should succeed."""
    client = logged_in_client
    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-MULTI-002",
            "room_number": "A01",
            "notes": "multi-bill meter",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-MULTI-002").first()
        assert meter is not None
        meter_id = meter.id

    for ym, pr, cr, amt in [("2026-07", "100", "150", "250"), ("2026-08", "150", "200", "300")]:
        response = client.post(
            "/electricity/bills/create",
            data={
                "property_id": seeded_data["property_id"],
                "meter_id": meter_id,
                "calc_method_id": seeded_data["calc_method_id"],
                "year_month": ym,
                "period_start": f"{ym}-01",
                "period_end": f"{ym}-31",
                "prev_reading": pr,
                "curr_reading": cr,
                "total_amount": amt,
                "public_amount": "50",
                "flow_amount": "0",
                "notes": f"multi-bill {ym}",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    with app.app_context():
        bills = ElectricityBill.query.filter_by(meter_id=meter_id).all()
        assert len(bills) == 2


@pytest.mark.skip(reason="Placeholder: electricity reading amount fallback logic (TBD).")
def test_electricity_reading_no_amount():
    ...


@pytest.mark.skip(reason="Placeholder: single-contract shared water allocation (TBD).")
def test_water_shared_single_contract():
    ...
