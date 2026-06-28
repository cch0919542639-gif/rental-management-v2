from app.core.errors import ConflictError
from app.core.db import db
from app.models import Room
from app.repositories import RoomRepository


class RoomService:
    @staticmethod
    def create_room(**payload):
        existing = RoomRepository.find_by_property_and_number(payload["property_id"], payload["room_number"])
        if existing:
            raise ConflictError("同一房產下房號不可重複")
        room = Room(**payload)
        db.session.add(room)
        db.session.commit()
        return room

    @staticmethod
    def update_room(room: Room, **payload):
        existing = RoomRepository.find_by_property_and_number(payload["property_id"], payload["room_number"])
        if existing and existing.id != room.id:
            raise ConflictError("同一房產下房號不可重複")
        for key, value in payload.items():
            setattr(room, key, value)
        db.session.commit()
        return room
