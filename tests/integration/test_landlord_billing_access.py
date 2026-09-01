import pytest

from app.core.db import db
from app.models import MonthlyBill, User


@pytest.fixture()
def landlord_client(client, seeded_data, app):
    with app.app_context():
        landlord = User(username="owner", name="Owner", role="landlord")
        landlord.set_password("owner123")
        db.session.add(landlord)
        db.session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "owner", "password": "owner123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return client


@pytest.mark.parametrize(
    "path",
    (
        "/billing/",
        "/billing/create",
        "/billing/1/edit",
        "/billing/contracts/1",
        "/billing/contracts/1/generate",
        "/billing/batch",
    ),
)
def test_landlord_cannot_access_billing_operations(landlord_client, path):
    assert landlord_client.get(path).status_code == 403


def test_landlord_cannot_change_bill_payment_status(landlord_client, seeded_data, app):
    response = landlord_client.post(f"/billing/{seeded_data['monthly_bill_id']}/toggle-paid")

    assert response.status_code == 403
    with app.app_context():
        bill = db.session.get(MonthlyBill, seeded_data["monthly_bill_id"])
        assert bill.paid is False
