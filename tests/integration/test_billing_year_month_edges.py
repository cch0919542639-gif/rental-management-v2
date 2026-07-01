"""
test_billing_year_month_edges.py

Phase 2 Round 2 — Year-month format edge cases in billing routes.

Covers:
  1. Billing list with DB format (YYYYMM)
  2. Billing list with UI format (YYYY-MM)
  3. Billing list with 'month' param (legacy alias)
  4. Billing create with UI format stored as YYYYMM in DB
  5. Cross-year boundary ordering
"""

from app.core.db import db
from app.core.year_month import to_db_year_month, to_ui_year_month, validate_ui_year_month
from app.models import MonthlyBill


def test_billing_list_db_format(app, logged_in_client, seeded_data):
    """Billing list should accept YYYYMM format."""
    client = logged_in_client
    response = client.get("/billing/?year_month=202606")
    assert response.status_code == 200


def test_billing_list_ui_format(app, logged_in_client, seeded_data):
    """Billing list should accept YYYY-MM format."""
    client = logged_in_client
    response = client.get("/billing/?year_month=2026-07")
    assert response.status_code == 200


def test_billing_list_month_param(app, logged_in_client, seeded_data):
    """Billing list should accept 'month' param (legacy alias)."""
    client = logged_in_client
    response = client.get("/billing/?month=2026-06")
    assert response.status_code == 200


def test_billing_create_ui_format_stored_as_db_format(app, logged_in_client, seeded_data):
    """Create a bill with YYYY-MM, verify stored as YYYYMM in DB."""
    client = logged_in_client
    response = client.post(
        "/billing/create",
        data={
            "contract_id": seeded_data["contract_id"],
            "year_month": "2026-11",
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
            "other_charges": "0",
            "notes": "UI format test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        bill = MonthlyBill.query.filter_by(
            contract_id=seeded_data["contract_id"], year_month="202611"
        ).first()
        assert bill is not None, "Bill not stored with DB-format year_month (YYYYMM)"


def test_billing_list_invalid_year_month(app, logged_in_client):
    """Invalid UI year_month should be rejected by the existing helper-backed flow."""
    client = logged_in_client
    invalid_value = "2026/13"
    assert validate_ui_year_month(invalid_value) is False

    response = client.get(f"/billing/?year_month={invalid_value}")
    assert response.status_code == 422
    assert "月份格式錯誤" in response.get_data(as_text=True)


def test_billing_year_month_boundary(app, logged_in_client, seeded_data):
    """Bills should remain queryable and correctly ordered across year boundaries."""
    client = logged_in_client
    december = to_db_year_month("2026-12")
    january = to_db_year_month("2027-01")

    with app.app_context():
        db.session.add(
            MonthlyBill(
                contract_id=seeded_data["contract_id"],
                year_month=december,
                rent=12000,
                electricity_amount=0,
                public_electricity=0,
                water_amount=0,
                other_charges=0,
                total=12000,
                paid=False,
            )
        )
        db.session.add(
            MonthlyBill(
                contract_id=seeded_data["contract_id"],
                year_month=january,
                rent=12000,
                electricity_amount=0,
                public_electricity=0,
                water_amount=0,
                other_charges=0,
                total=12000,
                paid=False,
            )
        )
        db.session.commit()

    response = client.get(f"/billing/?year_month={to_ui_year_month(january)}")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "2027-01" in html
    assert "2026-12" not in html
