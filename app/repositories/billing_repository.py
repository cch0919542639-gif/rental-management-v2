from sqlalchemy import func

from app.core.db import db
from app.core.year_month import to_db_year_month
from app.models import MonthlyBill


class BillingRepository:
    @staticmethod
    def list_for_contract(contract_id: int):
        return MonthlyBill.query.filter_by(contract_id=contract_id).order_by(MonthlyBill.year_month.desc()).all()

    @staticmethod
    def sum_total_for_month(year_month: str, *, paid: bool | None = None):
        query = db.session.query(func.sum(MonthlyBill.total)).filter(MonthlyBill.year_month == to_db_year_month(year_month))
        if paid is not None:
            query = query.filter(MonthlyBill.paid.is_(paid))
        return query.scalar() or 0

    @staticmethod
    def list_for_month(year_month: str):
        return (
            MonthlyBill.query.filter(MonthlyBill.year_month == to_db_year_month(year_month))
            .order_by(MonthlyBill.created_at.desc())
            .all()
        )
