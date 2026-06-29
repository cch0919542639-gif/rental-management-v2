from app.core.db import db
from app.core.errors import ConflictError
from app.models import Landlord
from sqlalchemy.exc import IntegrityError


class LandlordService:
    @staticmethod
    def create_landlord(**payload):
        landlord = Landlord(**payload)
        db.session.add(landlord)
        db.session.commit()
        return landlord

    @staticmethod
    def update_landlord(landlord: Landlord, **payload):
        for key, value in payload.items():
            setattr(landlord, key, value)
        db.session.commit()
        return landlord

    @staticmethod
    def delete_landlord(landlord: Landlord):
        try:
            db.session.delete(landlord)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise ConflictError("此房東仍有關聯資料，無法刪除") from exc
