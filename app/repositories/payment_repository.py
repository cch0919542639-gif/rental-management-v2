from app.models import PaymentRecord
from app.repositories._helpers import session_get_or_404


class PaymentRepository:
    @staticmethod
    def list_all():
        return PaymentRecord.query.order_by(PaymentRecord.created_at.desc()).all()

    @staticmethod
    def list_filtered(*, record_status=None, contract_id=None, monthly_bill_id=None, limit: int | None = None):
        query = PaymentRecord.query
        if record_status:
            query = query.filter(PaymentRecord.record_status == record_status)
        if contract_id:
            query = query.filter(PaymentRecord.contract_id == contract_id)
        if monthly_bill_id:
            query = query.filter(PaymentRecord.monthly_bill_id == monthly_bill_id)
        query = query.order_by(PaymentRecord.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def list_recent(limit: int = 20):
        return PaymentRecord.query.order_by(PaymentRecord.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_or_404(payment_id: int):
        return session_get_or_404(PaymentRecord, payment_id)

    @staticmethod
    def get_by_transaction_id(transaction_id: str):
        return PaymentRecord.query.filter_by(transaction_id=transaction_id).first()
