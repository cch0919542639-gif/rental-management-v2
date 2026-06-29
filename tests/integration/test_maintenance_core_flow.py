from app.core.db import db
from app.models.maintenance import MaintenanceRequest


def test_maintenance_create_and_transition_flow(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/maintenance/create",
        data={
            "room_id": seeded_data["room_id"],
            "issue_category": "facility",
            "priority": "high",
            "title": "Door lock broken",
            "description": "Main door lock cannot close",
            "reported_by_name": "Tenant One",
            "assigned_to_name": "Repair A",
            "estimated_cost": "300",
            "actual_cost": "0",
            "notes": "needs urgent check",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "維修單已建立" in response.get_data(as_text=True)

    with app.app_context():
        request = MaintenanceRequest.query.first()
        assert request is not None
        request_id = request.id
        assert request.status == "reported"

    response = client.post(f"/maintenance/{request_id}/transition/assigned", follow_redirects=True)
    assert response.status_code == 200
    response = client.post(f"/maintenance/{request_id}/transition/in_progress", follow_redirects=True)
    assert response.status_code == 200
    response = client.post(f"/maintenance/{request_id}/transition/resolved", follow_redirects=True)
    assert response.status_code == 200
    response = client.post(f"/maintenance/{request_id}/transition/closed", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        request = db.session.get(MaintenanceRequest, request_id)
        assert request.status == "closed"
        assert request.started_at is not None
        assert request.resolved_at is not None
        assert request.closed_at is not None

    response = client.get("/maintenance/")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Door lock broken" in text
    assert "closed" in text
