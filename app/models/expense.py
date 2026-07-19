from sqlalchemy.sql import func

from app.core.db import db
from app.models.base import BaseModel


class PropertyExpense(BaseModel):
    __tablename__ = "property_expenses"

    CATEGORIES = {"management_fee", "cleaning", "repair", "utility", "tax", "insurance", "supplies", "other"}
    TRANSITIONS = {"draft": {"posted", "cancelled"}, "posted": {"voided"}, "voided": set(), "cancelled": set()}

    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="RESTRICT"), nullable=False, index=True)
    transaction_date = db.Column(db.Date, nullable=False, index=True)
    category = db.Column(db.String(30), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payee = db.Column(db.String(100))
    reference_no = db.Column(db.String(100))
    notes = db.Column(db.Text)
    record_status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), index=True)
    voided_at = db.Column(db.DateTime)
    void_reason = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    property = db.relationship("Property", backref="property_expenses", lazy=True)
    created_by = db.relationship("User", foreign_keys=[created_by_id], lazy=True)
