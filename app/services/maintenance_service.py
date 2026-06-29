from datetime import UTC, datetime

from app.core.db import db
from app.models.maintenance import MaintenanceRequest
from app.repositories import MaintenanceRepository, RoomRepository


class MaintenanceService:
    TRANSITIONS = {
        "reported": {"assigned", "cancelled"},
        "assigned": {"in_progress", "cancelled"},
        "in_progress": {"resolved"},
        "resolved": {"closed"},
        "closed": set(),
        "cancelled": set(),
    }

    @staticmethod
    def list_requests():
        return MaintenanceRepository.list_all()

    @staticmethod
    def list_filtered_requests(**filters):
        return MaintenanceRepository.list_filtered(**filters)

    @staticmethod
    def list_open_requests(**filters):
        filters.pop("status", None)
        return MaintenanceRepository.list_open(**filters)

    @staticmethod
    def summary(**filters):
        summary = MaintenanceRepository.summary(**filters)
        room_id = filters.get("room_id")
        reported_from = filters.get("reported_from")
        reported_to = filters.get("reported_to")
        return {
            "request_count": summary.request_count or 0,
            "estimated_total": summary.estimated_total or 0,
            "actual_total": summary.actual_total or 0,
            "status_breakdown": MaintenanceRepository.status_breakdown(
                room_id=room_id,
                reported_from=reported_from,
                reported_to=reported_to,
            ),
        }

    @staticmethod
    def room_snapshot():
        return [
            {
                "room_id": room.id,
                "property_name": room.property.name,
                "room_number": room.room_number,
                "status": room.status,
                "notes": room.notes,
            }
            for room in RoomRepository.list_all()
        ]

    @staticmethod
    def list_for_room(room_id: int):
        return MaintenanceRepository.list_for_room(room_id)

    @staticmethod
    def create_request(**payload):
        request = MaintenanceRequest(
            room_id=payload["room_id"],
            issue_category=payload["issue_category"],
            priority=payload["priority"],
            title=payload["title"],
            description=payload.get("description"),
            reported_by_name=payload.get("reported_by_name"),
            assigned_to_name=payload.get("assigned_to_name"),
            estimated_cost=payload.get("estimated_cost") or 0,
            actual_cost=payload.get("actual_cost") or 0,
            notes=payload.get("notes"),
        )
        db.session.add(request)
        db.session.commit()
        return request

    @staticmethod
    def update_request(request, **payload):
        request.room_id = payload["room_id"]
        request.issue_category = payload["issue_category"]
        request.priority = payload["priority"]
        request.title = payload["title"]
        request.description = payload.get("description")
        request.reported_by_name = payload.get("reported_by_name")
        request.assigned_to_name = payload.get("assigned_to_name")
        request.estimated_cost = payload.get("estimated_cost") or 0
        request.actual_cost = payload.get("actual_cost") or 0
        request.notes = payload.get("notes")
        db.session.commit()
        return request

    @staticmethod
    def transition_status(request, next_status: str):
        allowed_statuses = MaintenanceService.TRANSITIONS.get(request.status, set())
        if next_status not in allowed_statuses:
            raise ValueError(f"Invalid maintenance transition: {request.status} -> {next_status}")

        request.status = next_status
        now = datetime.now(UTC).replace(tzinfo=None)
        if next_status == "in_progress" and request.started_at is None:
            request.started_at = now
        if next_status == "resolved" and request.resolved_at is None:
            request.resolved_at = now
        if next_status == "closed" and request.closed_at is None:
            request.closed_at = now
        db.session.commit()
        return request
