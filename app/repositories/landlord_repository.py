from app.models import Landlord
from app.repositories._helpers import session_get_or_404


class LandlordRepository:
    @staticmethod
    def list_all():
        return Landlord.query.order_by(Landlord.name.asc()).all()

    @staticmethod
    def get_or_404(landlord_id: int):
        return session_get_or_404(Landlord, landlord_id)

    @staticmethod
    def delete(landlord: Landlord):
        landlord.delete()
