from app.core.db import db
from app.core.errors import ConflictError, DomainValidationError
from app.models import WaterBill
from app.repositories import BillingRepository, ContractRepository
from app.services.billing_service import BillingService
from app.services.rate_policy_service import RatePolicyService
from app.services.utility_policy_resolver import UtilityPolicyResolver
from app.services.water_allocation_service import WaterAllocationService
from sqlalchemy.exc import IntegrityError


class WaterService:
    @staticmethod
    def _resolve_contract_for_monthly_bill(monthly_bill_id: int):
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)
        contract = ContractRepository.get_or_404(monthly_bill.contract_id)
        return monthly_bill, contract

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
        preview = WaterService.preview_shared_to_monthly_bill(monthly_bill_id=monthly_bill_id, water_bill=water_bill)
        monthly_bill.water_amount = preview["preview_water_amount"]
        monthly_bill.water_usage = preview["preview_water_usage"]
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

    @staticmethod
    def preview_shared_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill):
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
        total_usage = (water_bill.actual_usage_1 or 0) + (water_bill.actual_usage_2 or 0)
        preview_water_amount = WaterAllocationService.allocate_shared_by_stay_days(
            total_amount=water_bill.total_amount,
            contract_days=contract_days,
            total_days=total_days,
        )
        preview_water_usage = WaterAllocationService.allocate_shared_usage_by_stay_days(
            total_usage=total_usage,
            contract_days=contract_days,
            total_days=total_days,
        )
        return {
            "mode": "shared_by_stay_days",
            "monthly_bill": monthly_bill,
            "contract": contract,
            "contract_days": contract_days,
            "total_days": total_days,
            "total_usage": total_usage,
            "preview_water_amount": preview_water_amount,
            "preview_water_usage": preview_water_usage,
        }

    @staticmethod
    def preview_independent_to_monthly_bill(*, monthly_bill_id: int, amount):
        monthly_bill, contract = WaterService._resolve_contract_for_monthly_bill(monthly_bill_id)
        preview_water_amount = WaterAllocationService.allocate_independent_meter(amount=amount)
        return {
            "mode": "independent_meter",
            "monthly_bill": monthly_bill,
            "contract": contract,
            "preview_water_amount": preview_water_amount,
            "preview_water_usage": monthly_bill.water_usage or 0,
        }

    @staticmethod
    def preview_policy_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill):
        monthly_bill, contract = WaterService._resolve_contract_for_monthly_bill(monthly_bill_id)
        policy_code = UtilityPolicyResolver.resolve_water_policy(contract)
        if policy_code == UtilityPolicyResolver.WATER_BILL_BY_STAY_DAYS:
            preview = WaterService.preview_shared_to_monthly_bill(
                monthly_bill_id=monthly_bill_id,
                water_bill=water_bill,
            )
            preview["mode"] = "auto_policy"
            preview["resolved_policy"] = policy_code
            return preview

        if policy_code == UtilityPolicyResolver.WATER_FREE:
            return {
                "mode": "auto_policy",
                "resolved_policy": policy_code,
                "monthly_bill": monthly_bill,
                "contract": contract,
                "preview_water_amount": 0,
                "preview_water_usage": 0,
            }

        if policy_code == UtilityPolicyResolver.WATER_FIXED_MONTHLY:
            return {
                "mode": "auto_policy",
                "resolved_policy": policy_code,
                "monthly_bill": monthly_bill,
                "contract": contract,
                "preview_water_amount": RatePolicyService.resolve_water_rate(contract),
                "preview_water_usage": monthly_bill.water_usage or 0,
            }

        raise DomainValidationError("未知的水費策略，無法預覽")

    @staticmethod
    def post_policy_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill):
        preview = WaterService.preview_policy_to_monthly_bill(monthly_bill_id=monthly_bill_id, water_bill=water_bill)
        monthly_bill = preview["monthly_bill"]
        monthly_bill.water_amount = preview["preview_water_amount"]
        monthly_bill.water_usage = preview["preview_water_usage"]
        BillingService.calculate_total(monthly_bill)
        db.session.commit()
        return monthly_bill

    @staticmethod
    def preview_post_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill, mode: str, amount=None):
        if mode == "auto_policy":
            return WaterService.preview_policy_to_monthly_bill(
                monthly_bill_id=monthly_bill_id,
                water_bill=water_bill,
            )
        if mode == "shared_by_stay_days":
            return WaterService.preview_shared_to_monthly_bill(
                monthly_bill_id=monthly_bill_id,
                water_bill=water_bill,
            )
        if mode == "independent_meter":
            return WaterService.preview_independent_to_monthly_bill(
                monthly_bill_id=monthly_bill_id,
                amount=amount,
            )
        raise DomainValidationError("未知的水費預覽模式")

    @staticmethod
    def delete_water_bill(water_bill: WaterBill):
        try:
            db.session.delete(water_bill)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise ConflictError("此水費單仍有關聯資料，無法刪除") from exc
