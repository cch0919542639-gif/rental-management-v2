from sqlalchemy import func

from app.core.db import db
from app.models.maintenance import MaintenanceRequest
from app.repositories._helpers import session_get_or_404


class MaintenanceRepository:
    OPEN_STATUSES = ["reported", "assigned", "in_progress"]

    @staticmethod
    def _apply_filters(query, *, status=None, priority=None, room_id=None, reported_from=None, reported_to=None):
        if status:
            query = query.filter(MaintenanceRequest.status == status)
        if priority:
            query = query.filter(MaintenanceRequest.priority == priority)
        if room_id:
            query = query.filter(MaintenanceRequest.room_id == room_id)
        if reported_from:
            query = query.filter(func.date(MaintenanceRequest.reported_at) >= reported_from)
        if reported_to:
            query = query.filter(func.date(MaintenanceRequest.reported_at) <= reported_to)
        return query

    @staticmethod
    def list_all():
        return (
            MaintenanceRequest.query.order_by(
                MaintenanceRequest.reported_at.desc(),
                MaintenanceRequest.id.desc(),
            ).all()
        )

    @staticmethod
    def list_filtered(*, status=None, priority=None, room_id=None, reported_from=None, reported_to=None):
        query = MaintenanceRepository._apply_filters(
            MaintenanceRequest.query,
            status=status,
            priority=priority,
            room_id=room_id,
            reported_from=reported_from,
            reported_to=reported_to,
        )
        return query.order_by(MaintenanceRequest.reported_at.desc(), MaintenanceRequest.id.desc()).all()

    @staticmethod
    def list_open(*, priority=None, room_id=None, reported_from=None, reported_to=None):
        query = MaintenanceRequest.query.filter(MaintenanceRequest.status.in_(MaintenanceRepository.OPEN_STATUSES))
        query = MaintenanceRepository._apply_filters(
            query,
            priority=priority,
            room_id=room_id,
            reported_from=reported_from,
            reported_to=reported_to,
        )
        return query.order_by(MaintenanceRequest.reported_at.desc(), MaintenanceRequest.id.desc()).all()

    @staticmethod
    def summary(*, status=None, priority=None, room_id=None, reported_from=None, reported_to=None):
        query = MaintenanceRepository._apply_filters(
            db.session.query(
                func.count(MaintenanceRequest.id).label("request_count"),
                func.coalesce(func.sum(MaintenanceRequest.estimated_cost), 0).label("estimated_total"),
                func.coalesce(func.sum(MaintenanceRequest.actual_cost), 0).label("actual_total"),
            ),
            status=status,
            priority=priority,
            room_id=room_id,
            reported_from=reported_from,
            reported_to=reported_to,
        )
        return query.one()

    @staticmethod
    def status_breakdown(*, room_id=None, reported_from=None, reported_to=None):
        query = MaintenanceRepository._apply_filters(
            db.session.query(
                MaintenanceRequest.status.label("status"),
                func.count(MaintenanceRequest.id).label("request_count"),
                func.coalesce(func.sum(MaintenanceRequest.estimated_cost), 0).label("estimated_total"),
                func.coalesce(func.sum(MaintenanceRequest.actual_cost), 0).label("actual_total"),
            ),
            room_id=room_id,
            reported_from=reported_from,
            reported_to=reported_to,
        )
        return (
            query.group_by(MaintenanceRequest.status)
            .order_by(MaintenanceRequest.status.asc())
            .all()
        )

    @staticmethod
    def list_open_legacy():
        return (
            MaintenanceRequest.query.filter(
                MaintenanceRequest.status.in_(["reported", "assigned", "in_progress"])
            )
            .order_by(MaintenanceRequest.reported_at.desc(), MaintenanceRequest.id.desc())
            .all()
        )

    @staticmethod
    def list_for_room(room_id: int):
        return (
            MaintenanceRequest.query.filter_by(room_id=room_id)
            .order_by(MaintenanceRequest.reported_at.desc(), MaintenanceRequest.id.desc())
            .all()
        )

    @staticmethod
    def get_or_404(request_id: int):
        return session_get_or_404(MaintenanceRequest, request_id)
