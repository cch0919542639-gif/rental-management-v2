from app.models import Landlord


class LandlordRepository:
    @staticmethod
    def list_all():
        return Landlord.query.order_by(Landlord.name.asc()).all()

    @staticmethod
    def get_or_404(landlord_id: int):
        return Landlord.query.get_or_404(landlord_id)
