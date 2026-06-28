from sqlalchemy import func

from app.core.db import db
from app.core.year_month import to_db_year_month
from app.models import MonthlyBill
from app.repositories._helpers import session_get_or_404


class BillingRepository:
    @staticmethod
    def list_all():
        return MonthlyBill.query.order_by(MonthlyBill.year_month.desc(), MonthlyBill.created_at.desc()).all()

    @staticmethod
    def list_for_contract(contract_id: int):
        return MonthlyBill.query.filter_by(contract_id=contract_id).order_by(MonthlyBill.year_month.desc()).all()

    @staticmethod
    def get_or_404(monthly_bill_id: int):
        return session_get_or_404(MonthlyBill, monthly_bill_id)

    @staticmethod
    def find_by_contract_and_month(contract_id: int, year_month: str):
        return MonthlyBill.query.filter_by(contract_id=contract_id, year_month=to_db_year_month(year_month)).first()

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
