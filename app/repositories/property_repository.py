from app.models import Property
from app.repositories._helpers import session_get_or_404


class PropertyRepository:
    @staticmethod
    def list_all():
        return Property.query.order_by(Property.name.asc()).all()

    @staticmethod
    def get_or_404(property_id: int):
        return session_get_or_404(Property, property_id)
