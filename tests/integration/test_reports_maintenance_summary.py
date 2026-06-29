from app.core.db import db
from app.models.maintenance import MaintenanceRequest


def test_reports_maintenance_summary_renders_property_and_status_totals(app, logged_in_client, seeded_data):
    client = logged_in_client

    with app.app_context():
        db.session.add_all(
            [
                MaintenanceRequest(
                    room_id=seeded_data["room_id"],
                    status="reported",
                    issue_category="facility",
                    priority="high",
                    title="Door lock",
                    estimated_cost=300,
                    actual_cost=0,
                ),
                MaintenanceRequest(
                    room_id=seeded_data["room_id"],
                    status="closed",
                    issue_category="water",
                    priority="medium",
                    title="Pipe leak",
                    estimated_cost=100,
                    actual_cost=80,
                ),
            ]
        )
        db.session.commit()

    response = client.get("/reports/maintenance")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "維修彙總" in text
    assert "North House" in text
    assert "reported" in text
    assert "closed" in text
    assert "400.00" in text or "400" in text
