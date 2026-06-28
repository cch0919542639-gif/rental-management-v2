from app.core.db import TimestampMixin, db


class BaseModel(TimestampMixin, db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
