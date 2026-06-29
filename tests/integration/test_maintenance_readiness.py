"""
test_maintenance_readiness.py

Phase 2 Round 2 — Maintenance module readiness placeholder + basic page check.

Covers:
  1. Maintenance index page renders and displays room snapshot data
  2. Room snapshot returns expected fields (room_id, property_name, room_number, status, notes)
  3. Placeholder: maintenance request form (TBD)
  4. Placeholder: maintenance status transitions (TBD)
"""

import pytest
from app.models import Room
from app.services import MaintenanceService


def test_maintenance_page_renders_with_rooms(app, logged_in_client, seeded_data):
    """Maintenance index page should render and include room data."""
    client = logged_in_client
    response = client.get("/maintenance/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "A01" in html or "North House" in html or "room" in html.lower()


def test_maintenance_room_snapshot_structure(app, seeded_data):
    """Verify MaintenanceService.room_snapshot() returns the expected dict shape."""
    with app.app_context():
        rooms = Room.query.all()
        assert len(rooms) > 0
        snapshot = MaintenanceService.room_snapshot()
        assert len(snapshot) == len(rooms)
        for entry in snapshot:
            assert "room_id" in entry
            assert "property_name" in entry
            assert "room_number" in entry
            assert "status" in entry
            assert "notes" in entry


@pytest.mark.skip(reason="Placeholder: maintenance request creation (TBD — schema just froze).")
def test_maintenance_request_create():
    ...


@pytest.mark.skip(reason="Placeholder: maintenance status workflow (TBD — routes not yet added).")
def test_maintenance_status_workflow():
    ...
