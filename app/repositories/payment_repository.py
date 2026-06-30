from datetime import date

from app.models import PaymentRecord
from app.repositories._helpers import session_get_or_404


class PaymentRepository:
    @staticmethod
    def list_all():
        return PaymentRecord.query.order_by(PaymentRecord.created_at.desc()).all()

    @staticmethod
    def list_recent(limit: int = 20):
        return PaymentRecord.query.order_by(PaymentRecord.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_or_404(payment_id: int):
        return session_get_or_404(PaymentRecord, payment_id)

    @staticmethod
    def get_by_transaction_id(transaction_id: str):
        return PaymentRecord.query.filter_by(transaction_id=transaction_id).first()

    @staticmethod
    def list_filtered(
        *,
        contract_id=None,
        monthly_bill_id=None,
        record_status=None,
        transaction_id=None,
        payer_name=None,
        date_from=None,
        date_to=None,
        limit=None,
        offset=None,
    ):
        query = PaymentRecord.query
        if contract_id not in (None, ""):
            query = query.filter(PaymentRecord.contract_id == int(contract_id))
        if monthly_bill_id not in (None, ""):
            query = query.filter(PaymentRecord.monthly_bill_id == int(monthly_bill_id))
        if record_status:
            query = query.filter(PaymentRecord.record_status == record_status)
        if transaction_id:
            query = query.filter(PaymentRecord.transaction_id == transaction_id)
        if payer_name:
            query = query.filter(PaymentRecord.payer_name.contains(payer_name))
        if date_from:
            if not isinstance(date_from, date):
                date_from = date.fromisoformat(str(date_from))
            query = query.filter(PaymentRecord.transaction_date >= date_from)
        if date_to:
            if not isinstance(date_to, date):
                date_to = date.fromisoformat(str(date_to))
            query = query.filter(PaymentRecord.transaction_date <= date_to)

        query = query.order_by(PaymentRecord.created_at.desc())
        if offset not in (None, ""):
            query = query.offset(int(offset))
        if limit not in (None, ""):
            query = query.limit(int(limit))
        return query.all()
