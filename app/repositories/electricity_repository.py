from app.models import CalcMethod, ElectricityBill, ElectricityMeter, ElectricityReading
from app.repositories._helpers import session_get_or_404


class ElectricityMeterRepository:
    @staticmethod
    def list_all():
        return ElectricityMeter.query.order_by(ElectricityMeter.property_id.asc(), ElectricityMeter.id.asc()).all()

    @staticmethod
    def get_or_404(meter_id: int):
        return session_get_or_404(ElectricityMeter, meter_id)


class ElectricityBillRepository:
    @staticmethod
    def list_all():
        return ElectricityBill.query.order_by(ElectricityBill.period_start.desc(), ElectricityBill.created_at.desc()).all()

    @staticmethod
    def get_or_404(bill_id: int):
        return session_get_or_404(ElectricityBill, bill_id)


class ElectricityReadingRepository:
    @staticmethod
    def list_for_bill(bill_id: int):
        return ElectricityReading.query.filter_by(bill_id=bill_id).order_by(ElectricityReading.id.asc()).all()


class CalcMethodRepository:
    @staticmethod
    def list_active():
        return CalcMethod.query.filter_by(is_active=True).order_by(CalcMethod.name.asc()).all()

    @staticmethod
    def get_or_404(calc_method_id: int):
        return session_get_or_404(CalcMethod, calc_method_id)
