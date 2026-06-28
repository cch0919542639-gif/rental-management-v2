from sqlalchemy.sql import func

from app.core.db.extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
