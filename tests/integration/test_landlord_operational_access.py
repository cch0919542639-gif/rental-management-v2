import pytest

from app.core.db import db
from app.models import User


@pytest.fixture()
def landlord_client(client, app):
    with app.app_context():
        landlord = User(username="owner-operations", name="Owner", role="landlord")
        landlord.set_password("owner123")
        db.session.add(landlord)
        db.session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "owner-operations", "password": "owner123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return client


@pytest.mark.parametrize(
    "path",
    (
        "/properties/",
        "/properties/create",
        "/properties/1/edit",
        "/tenants/",
        "/tenants/create",
        "/tenants/1/edit",
        "/contracts/",
        "/contracts/create",
        "/contracts/1/edit",
        "/payments/",
        "/payments/create",
        "/payments/1/verify",
        "/payments/1/reject",
        "/payments/1/link",
    ),
)
def test_landlord_cannot_access_operational_routes(landlord_client, path):
    assert landlord_client.get(path).status_code == 403


@pytest.mark.parametrize(
    "path",
    (
        "/tenants/1/delete",
        "/contracts/1/terminate",
    ),
)
def test_landlord_cannot_mutate_operational_records(landlord_client, path):
    assert landlord_client.post(path).status_code == 403
