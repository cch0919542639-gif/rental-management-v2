from sqlalchemy.sql import func

from app.core.db import db
from app.models.base import BaseModel


class MaintenanceRequest(BaseModel):
    __tablename__ = "maintenance_requests"

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="reported", index=True)
    issue_category = db.Column(db.String(20), default="other")
    priority = db.Column(db.String(20), default="medium", index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    reported_by_name = db.Column(db.String(100))
    reported_at = db.Column(db.DateTime, server_default=func.now(), nullable=False, index=True)
    assigned_to_name = db.Column(db.String(100))
    started_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    estimated_cost = db.Column(db.Numeric(10, 2), default=0)
    actual_cost = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    room = db.relationship("Room", backref="maintenance_requests", lazy=True)
