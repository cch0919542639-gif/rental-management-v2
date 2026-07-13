from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func

from app.core.db import db
from app.core.year_month import to_db_year_month
from app.models import MonthlyBill
from app.repositories._helpers import session_get_or_404
from app.repositories.payment_repository import PaymentRepository


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
            query = query.filter(func.coalesce(MonthlyBill.paid, False).is_(paid))
        return query.scalar() or 0

    @staticmethod
    def prior_unpaid_balance(contract_id: int, year_month: str):
        """Return unique unpaid charges before a new statement, without carry duplication."""
        bills = (
            MonthlyBill.query.filter(MonthlyBill.contract_id == contract_id)
            .filter(MonthlyBill.year_month < to_db_year_month(year_month))
            .order_by(MonthlyBill.year_month.asc(), MonthlyBill.id.asc())
            .all()
        )
        balance = Decimal("0")
        for bill in bills:
            recorded_prior_balance = Decimal(str(bill.previous_balance or 0))
            # Imported statements may begin after older, unavailable history.
            # Their recorded prior balance is the authoritative ledger snapshot.
            if balance != recorded_prior_balance:
                balance = recorded_prior_balance
            linked_amount = Decimal(str(PaymentRepository.linked_amount_for_bill(bill.id) or 0))
            if bool(bill.paid) and linked_amount == 0:
                # Legacy/manual toggle-paid records predate PaymentRecord. Keep
                # their explicit full-settlement meaning during the transition.
                balance = Decimal("0")
                continue
            current_period_due = Decimal(str(bill.total or 0)) - Decimal(str(bill.previous_balance or 0))
            balance += current_period_due
            balance -= linked_amount
        return balance.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    @staticmethod
    def list_for_month(year_month: str):
        return (
            MonthlyBill.query.filter(MonthlyBill.year_month == to_db_year_month(year_month))
            .order_by(MonthlyBill.created_at.desc())
            .all()
        )
