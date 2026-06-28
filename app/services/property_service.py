from app.core.db import db
from app.models import Property


class PropertyService:
    @staticmethod
    def create_property(**payload):
        prop = Property(**payload)
        db.session.add(prop)
        db.session.commit()
        return prop

    @staticmethod
    def update_property(prop: Property, **payload):
        for key, value in payload.items():
            setattr(prop, key, value)
        db.session.commit()
        return prop
