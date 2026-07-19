from sqlalchemy import func

from app.core.db import db
from app.models.expense import PropertyExpense
from app.repositories._helpers import session_get_or_404


class PropertyExpenseRepository:
    @staticmethod
    def get_or_404(expense_id: int):
        return session_get_or_404(PropertyExpense, expense_id)

    @staticmethod
    def list_for_property(property_id: int, *, status: str | None = None):
        query = PropertyExpense.query.filter_by(property_id=property_id)
        if status:
            query = query.filter_by(record_status=status)
        return query.order_by(PropertyExpense.transaction_date.desc(), PropertyExpense.id.desc()).all()

    @staticmethod
    def list_filtered(*, property_id: int | None = None, status: str | None = None, category: str | None = None):
        query = PropertyExpense.query
        if property_id:
            query = query.filter_by(property_id=property_id)
        if status:
            query = query.filter_by(record_status=status)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(PropertyExpense.transaction_date.desc(), PropertyExpense.id.desc()).all()

    @staticmethod
    def posted_total(*, property_id: int | None = None):
        query = db.session.query(func.coalesce(func.sum(PropertyExpense.amount), 0)).filter(
            PropertyExpense.record_status == "posted"
        )
        if property_id:
            query = query.filter(PropertyExpense.property_id == property_id)
        return query.scalar()
