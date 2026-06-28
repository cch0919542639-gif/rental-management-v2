from app.models import PaymentRecord


class PaymentRepository:
    @staticmethod
    def list_recent(limit: int = 20):
        return PaymentRecord.query.order_by(PaymentRecord.created_at.desc()).limit(limit).all()
