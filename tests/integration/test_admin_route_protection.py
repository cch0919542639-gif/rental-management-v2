from app.core.db import db
from app.models import User


def _login_as_viewer(client):
    response = client.post(
        "/auth/login",
        data={"username": "viewer", "password": "viewer123"},
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_viewer_cannot_access_admin_html_routes(app, client, seeded_data):
    with app.app_context():
        viewer = User(username="viewer", name="Viewer", role="viewer")
        viewer.set_password("viewer123")
        db.session.add(viewer)
        db.session.commit()

    _login_as_viewer(client)

    response = client.get("/billing/create")
    assert response.status_code == 403

    response = client.get("/maintenance/create")
    assert response.status_code == 403


def test_viewer_cannot_call_admin_payment_api(app, client, seeded_data):
    with app.app_context():
        viewer = User(username="viewer", name="Viewer", role="viewer")
        viewer.set_password("viewer123")
        db.session.add(viewer)
        db.session.commit()

    _login_as_viewer(client)

    response = client.post(
        "/api/payment-records/",
        json={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "12000.00",
        },
    )
    assert response.status_code == 403
