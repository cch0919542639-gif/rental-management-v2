from flask import flash

from app.core.db import db
from app.models import Landlord
from app.repositories import LandlordRepository


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
    def delete_landlord(landlord_id: int):
        landlord = LandlordRepository.get_or_404(landlord_id)
        if landlord.properties:
            flash(f"房东「{landlord.name}」尚有 {len(landlord.properties)} 笔物件，无法删除", "error")
            return None
        LandlordRepository.delete(landlord)
        flash("房东已删除", "success")
        return landlord
