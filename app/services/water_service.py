from app.core.db import db
from app.core.errors import DomainValidationError
from app.models import WaterBill
from app.repositories import BillingRepository, ContractRepository
from app.services.billing_service import BillingService
from app.services.water_allocation_service import WaterAllocationService


class WaterService:
    @staticmethod
    def create_water_bill(**payload):
        if payload["billing_end"] <= payload["billing_start"]:
            raise DomainValidationError("水費帳期結束日必須晚於開始日")
        if (payload.get("total_amount") or 0) < 0:
            raise DomainValidationError("水費總額不可小於 0")

        water_bill = WaterBill(**payload)
        db.session.add(water_bill)
        db.session.commit()
        return water_bill

    @staticmethod
    def update_water_bill(water_bill: WaterBill, **payload):
        if payload["billing_end"] <= payload["billing_start"]:
            raise DomainValidationError("水費帳期結束日必須晚於開始日")
        if (payload.get("total_amount") or 0) < 0:
            raise DomainValidationError("水費總額不可小於 0")

        for key, value in payload.items():
            setattr(water_bill, key, value)
        db.session.commit()
        return water_bill

    @staticmethod
    def post_shared_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill):
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)
        contract = ContractRepository.get_or_404(monthly_bill.contract_id)
        active_contracts = [
            item
            for item in ContractRepository.list_active()
            if item.room.property_id == water_bill.property_id
        ]

        contract_days = WaterAllocationService.overlap_days(
            contract=contract,
            billing_start=water_bill.billing_start,
            billing_end=water_bill.billing_end,
        )
        total_days = sum(
            WaterAllocationService.overlap_days(
                contract=item,
                billing_start=water_bill.billing_start,
                billing_end=water_bill.billing_end,
            )
            for item in active_contracts
        )
        monthly_bill.water_amount = WaterAllocationService.allocate_shared_by_stay_days(
            total_amount=water_bill.total_amount,
            contract_days=contract_days,
            total_days=total_days,
        )
        BillingService.calculate_total(monthly_bill)
        db.session.commit()
        return monthly_bill

    @staticmethod
    def post_independent_to_monthly_bill(*, monthly_bill_id: int, amount):
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)
        monthly_bill.water_amount = WaterAllocationService.allocate_independent_meter(amount=amount)
        BillingService.calculate_total(monthly_bill)
        db.session.commit()
        return monthly_bill
