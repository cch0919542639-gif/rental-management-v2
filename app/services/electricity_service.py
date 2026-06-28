from decimal import Decimal

from app.core.db import db
from app.core.errors import DomainValidationError
from app.core.year_month import to_db_year_month
from app.models import ElectricityBill, ElectricityMeter, ElectricityReading, MonthlyBill
from app.repositories import BillingRepository
from app.services.billing_service import BillingService


class ElectricityService:
    @staticmethod
    def create_meter(**payload):
        meter = ElectricityMeter(**payload)
        db.session.add(meter)
        db.session.commit()
        return meter

    @staticmethod
    def update_meter(meter: ElectricityMeter, **payload):
        for key, value in payload.items():
            setattr(meter, key, value)
        db.session.commit()
        return meter

    @staticmethod
    def create_bill(**payload):
        if payload["period_end"] <= payload["period_start"]:
            raise DomainValidationError("電費帳期結束日必須晚於開始日")

        prev_reading = Decimal(str(payload.get("prev_reading") or 0))
        curr_reading = Decimal(str(payload.get("curr_reading") or 0))
        total_usage = curr_reading - prev_reading
        if total_usage < 0:
            raise DomainValidationError("電表讀數不可倒退")

        payload["year_month"] = to_db_year_month(payload["year_month"])
        payload["total_usage"] = total_usage
        bill = ElectricityBill(status="pending", **payload)
        db.session.add(bill)
        db.session.commit()
        return bill

    @staticmethod
    def add_reading(bill: ElectricityBill, **payload):
        prev_reading = Decimal(str(payload.get("prev_reading") or 0))
        curr_reading = Decimal(str(payload.get("curr_reading") or 0))
        usage = curr_reading - prev_reading
        if usage < 0:
            raise DomainValidationError("抄表 usage 不可為負值")

        payload["usage"] = usage
        confirmed_amount = payload.get("confirmed_amount")
        payload["calculated_amount"] = payload.get("calculated_amount") or 0
        if confirmed_amount is not None:
            payload["confirmed_amount"] = confirmed_amount

        reading = ElectricityReading(bill_id=bill.id, **payload)
        db.session.add(reading)
        db.session.commit()
        return reading

    @staticmethod
    def calculate_bill(bill: ElectricityBill):
        bill.status = "calculated"
        db.session.commit()
        return bill

    @staticmethod
    def post_to_monthly_bill(*, monthly_bill: MonthlyBill, reading: ElectricityReading, public_electricity=0):
        monthly_bill.electricity_prev = reading.prev_reading
        monthly_bill.electricity_curr = reading.curr_reading
        monthly_bill.electricity_usage = reading.usage
        monthly_bill.electricity_amount = reading.confirmed_amount or reading.calculated_amount
        monthly_bill.public_electricity = public_electricity or 0
        BillingService.calculate_total(monthly_bill)
        db.session.commit()
        return monthly_bill

    @staticmethod
    def post_reading_to_monthly_bill(*, monthly_bill_id: int, reading: ElectricityReading, public_electricity=0):
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)
        return ElectricityService.post_to_monthly_bill(
            monthly_bill=monthly_bill,
            reading=reading,
            public_electricity=public_electricity,
        )
