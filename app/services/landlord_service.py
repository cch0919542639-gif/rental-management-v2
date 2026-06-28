from app.core.db import db
from app.models import Landlord


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
