from app.core.db import db
from app.models import WaterBill
from app.repositories._helpers import session_get_or_404


class WaterBillRepository:
    @staticmethod
    def list_all():
        return WaterBill.query.order_by(WaterBill.billing_start.desc(), WaterBill.created_at.desc()).all()

    @staticmethod
    def get_or_404(water_bill_id: int):
        return session_get_or_404(WaterBill, water_bill_id)

    @staticmethod
    def delete(water_bill: WaterBill):
        db.session.delete(water_bill)
        db.session.commit()
