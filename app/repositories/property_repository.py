from app.models import Property


class PropertyRepository:
    @staticmethod
    def list_all():
        return Property.query.order_by(Property.name.asc()).all()

    @staticmethod
    def get_or_404(property_id: int):
        return Property.query.get_or_404(property_id)
