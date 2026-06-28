from app.core.db import db
from app.models import MonthlyBill


def test_billing_create_generate_and_toggle_paid(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/billing/create",
        data={
            "contract_id": seeded_data["contract_id"],
            "year_month": "2026-07",
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
            "other_charges": "100",
            "other_desc": "cleaning",
            "notes": "manual create",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        july = MonthlyBill.query.filter_by(contract_id=seeded_data["contract_id"], year_month="202607").first()
        assert july is not None
        assert float(july.total) == 12100.0
        july_id = july.id

    response = client.post(f"/billing/{july_id}/toggle-paid", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        july = db.session.get(MonthlyBill, july_id)
        assert july.paid is True

    response = client.post(
        f"/billing/contracts/{seeded_data['contract_id']}/generate",
        data={"year_month": "2026-08", "contract_id": seeded_data["contract_id"]},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        august = MonthlyBill.query.filter_by(contract_id=seeded_data["contract_id"], year_month="202608").first()
        assert august is not None

    response = client.post(
        "/billing/batch",
        data={"year_month": "2026-09"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        september = MonthlyBill.query.filter_by(contract_id=seeded_data["contract_id"], year_month="202609").first()
        assert september is not None
