from app.models.maintenance import MaintenanceRequest
from app.repositories._helpers import session_get_or_404


class MaintenanceRepository:
    @staticmethod
    def list_all():
        return (
            MaintenanceRequest.query.order_by(
                MaintenanceRequest.reported_at.desc(),
                MaintenanceRequest.id.desc(),
            ).all()
        )

    @staticmethod
    def list_open():
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
