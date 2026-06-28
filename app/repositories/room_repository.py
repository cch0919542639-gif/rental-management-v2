from sqlalchemy import func

from app.core.db import db
from app.models import Room
from app.repositories._helpers import session_get_or_404


class RoomRepository:
    @staticmethod
    def list_all():
        return Room.query.order_by(Room.property_id.asc(), Room.room_number.asc()).all()

    @staticmethod
    def get_or_404(room_id: int):
        return session_get_or_404(Room, room_id)

    @staticmethod
    def find_by_property_and_number(property_id: int, room_number: str):
        return Room.query.filter_by(property_id=property_id, room_number=room_number).first()

    @staticmethod
    def count_all():
        return db.session.query(func.count(Room.id)).scalar() or 0

    @staticmethod
    def count_by_status(status: str):
        return db.session.query(func.count(Room.id)).filter(Room.status == status).scalar() or 0
