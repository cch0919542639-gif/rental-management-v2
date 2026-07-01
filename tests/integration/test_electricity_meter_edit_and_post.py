"""
test_electricity_meter_edit_and_post.py

Phase 2 — Electricity: meter editing, bill posting to monthly bill, edge cases.

Covers:
  1. Create a meter -> edit it (update notes -> verify)
  2. Create a bill with a reading -> post reading to monthly bill
     -> verify monthly_bill.electricity_amount is updated
  3. Placeholder: bill status transitions (skip)

Constraints:
  - Does NOT modify ElectricityService or any electricity model.
  - Does NOT alter calc_method or billing rules.
"""

import pytest
from app.core.db import db
from app.core.year_month import to_db_year_month
from app.models import ElectricityBill, ElectricityMeter, MonthlyBill
from app.repositories import ElectricityReadingRepository


def test_electricity_meter_edit(app, logged_in_client, seeded_data):
    """Create a meter, edit its notes, and verify the update."""
    client = logged_in_client

    # Create a meter
    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-EDIT-001",
            "room_number": "A01",
            "notes": "initial notes",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-EDIT-001").first()
        assert meter is not None
        meter_id = meter.id
        assert meter.notes == "initial notes"

    # Edit the meter
    response = client.post(
        f"/electricity/meters/{meter_id}/edit",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-EDIT-001",
            "room_number": "A01",
            "is_main": False,
            "notes": "updated notes",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-EDIT-001").first()
        assert meter.notes == "updated notes"


def test_electricity_bill_post_to_monthly_bill(app, logged_in_client, seeded_data):
    """Create bill + reading -> calculate -> post to monthly bill -> verify amount."""
    client = logged_in_client

    # Create a meter first
    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-POST-001",
            "room_number": "A01",
            "notes": "post test meter",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-POST-001").first()
        meter_id = meter.id

    # Create a bill
    response = client.post(
        "/electricity/bills/create",
        data={
            "property_id": seeded_data["property_id"],
            "meter_id": meter_id,
            "calc_method_id": seeded_data["calc_method_id"],
            "year_month": "2026-06",
            "period_start": "2026-06-01",
            "period_end": "2026-06-30",
            "prev_reading": "200",
            "curr_reading": "250",
            "total_amount": "600",
            "public_amount": "100",
            "flow_amount": "0",
            "notes": "post test bill",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        bill = ElectricityBill.query.filter_by(
            prev_reading=200, curr_reading=250
        ).first()
        assert bill is not None
        bill_id = bill.id

    # Create a reading for the bill
    response = client.post(
        f"/electricity/bills/{bill_id}/readings/create",
        data={
            "meter_id": meter_id,
            "room_id": seeded_data["room_id"],
            "prev_reading": "200",
            "curr_reading": "250",
            "calculated_amount": "500",
            "confirmed_amount": "500",
            "notes": "post test reading",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Calculate
    response = client.post(
        f"/electricity/bills/{bill_id}/calculate",
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        bill = db.session.get(ElectricityBill, bill_id)
        assert bill.status == "calculated"

    # Post the reading to the monthly bill
    with app.app_context():
        readings = ElectricityReadingRepository.list_for_bill(bill_id)
        reading_id = readings[0].id if readings else None
        assert reading_id is not None, "No reading found after calculate"

    response = client.post(
        f"/electricity/bills/{bill_id}/post",
        data={
            "reading_id": reading_id,
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "public_electricity": "0",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Verify monthly bill now has electricity_amount > 0
    with app.app_context():
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert monthly_bill.electricity_amount > 0, (
            f"Expected electricity_amount > 0, got {monthly_bill.electricity_amount}"
        )


def test_electricity_bill_status_transitions(app, logged_in_client, seeded_data):
    """Bill should stay within the frozen pending -> calculated status machine."""
    client = logged_in_client

    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-STATUS-001",
            "room_number": "A01",
            "notes": "status test meter",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-STATUS-001").first()
        meter_id = meter.id

    response = client.post(
        "/electricity/bills/create",
        data={
            "property_id": seeded_data["property_id"],
            "meter_id": meter_id,
            "calc_method_id": seeded_data["calc_method_id"],
            "year_month": "2026-09",
            "period_start": "2026-09-01",
            "period_end": "2026-09-30",
            "prev_reading": "10",
            "curr_reading": "30",
            "total_amount": "100",
            "public_amount": "0",
            "flow_amount": "0",
            "notes": "status test bill",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        bill = ElectricityBill.query.filter_by(notes="status test bill").first()
        assert bill.status == "pending"
        bill_id = bill.id

    response = client.post(
        f"/electricity/bills/{bill_id}/readings/create",
        data={
            "meter_id": meter_id,
            "room_id": seeded_data["room_id"],
            "prev_reading": "10",
            "curr_reading": "30",
            "calculated_amount": "100",
            "confirmed_amount": "100",
            "notes": "status test reading",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(f"/electricity/bills/{bill_id}/calculate", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        bill = db.session.get(ElectricityBill, bill_id)
        assert bill.status == "calculated"

    readings = ElectricityReadingRepository.list_for_bill(bill_id)
    response = client.post(
        f"/electricity/bills/{bill_id}/post",
        data={
            "reading_id": readings[0].id,
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "public_electricity": "0",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        bill = db.session.get(ElectricityBill, bill_id)
        monthly_bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert bill.status == "calculated"
        assert monthly_bill.electricity_amount == readings[0].confirmed_amount


def test_electricity_year_month_format(app, logged_in_client, seeded_data):
    """Electricity bill should store UI year_month as DB format via helper-backed service."""
    client = logged_in_client

    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-YM-001",
            "room_number": "A01",
            "notes": "ym test meter",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-YM-001").first()
        meter_id = meter.id

    response = client.post(
        "/electricity/bills/create",
        data={
            "property_id": seeded_data["property_id"],
            "meter_id": meter_id,
            "calc_method_id": seeded_data["calc_method_id"],
            "year_month": "2026-10",
            "period_start": "2026-10-01",
            "period_end": "2026-10-31",
            "prev_reading": "0",
            "curr_reading": "10",
            "total_amount": "50",
            "public_amount": "0",
            "flow_amount": "0",
            "notes": "ym test bill",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        bill = ElectricityBill.query.filter_by(notes="ym test bill").first()
        assert bill.year_month == to_db_year_month("2026-10")
