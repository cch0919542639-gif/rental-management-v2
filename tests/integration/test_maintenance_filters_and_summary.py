from app.core.db import db
from app.models import Room
from app.models.maintenance import MaintenanceRequest


def test_maintenance_filters_open_and_room_scoped(app, logged_in_client, seeded_data):
    client = logged_in_client

    with app.app_context():
        base_room = db.session.get(Room, seeded_data["room_id"])
        room_two = Room(
            property_id=base_room.property_id,
            room_number="A02",
            rent=base_room.rent,
            deposit=base_room.deposit,
            status="vacant",
        )
        db.session.add(room_two)
        db.session.flush()

        req1 = MaintenanceRequest(
            room_id=base_room.id,
            status="reported",
            issue_category="facility",
            priority="high",
            title="Leak one",
            estimated_cost=200,
            actual_cost=0,
        )
        req2 = MaintenanceRequest(
            room_id=room_two.id,
            status="closed",
            issue_category="water",
            priority="low",
            title="Leak two",
            estimated_cost=100,
            actual_cost=80,
        )
        db.session.add_all([req1, req2])
        db.session.commit()
        room_two_id = room_two.id

    response = client.get("/maintenance/?status=reported&priority=high")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Leak one" in text
    assert "Leak two" not in text
    assert "筆數" in text
    assert "預估成本" in text

    response = client.get("/maintenance/open")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Open 維修單" in text
    assert "Leak one" in text
    assert "Leak two" not in text

    response = client.get(f"/maintenance/rooms/{room_two_id}")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "房間維修單" in text
    assert "Leak two" in text
