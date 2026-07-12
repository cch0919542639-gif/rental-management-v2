from decimal import Decimal

from app.core.db import db
from app.core.errors import DomainValidationError
from app.core.year_month import to_db_year_month
from app.models import ElectricityBill, ElectricityMeter, ElectricityReading, MonthlyBill
from app.repositories import BillingRepository, ContractRepository, ElectricityReadingRepository
from app.services.billing_service import BillingService
from app.services.rate_policy_service import RatePolicyService
from app.services.utility_policy_resolver import UtilityPolicyResolver


class ElectricityService:
    @staticmethod
    def _resolve_contract(room_id: int | None):
        if not room_id:
            return None
        return ContractRepository.active_for_room(room_id)

    @staticmethod
    def _resolve_contract_for_period(room_id: int | None, *, period_start, period_end):
        if not room_id:
            return None
        candidates = [
            item
            for item in ContractRepository.list_active()
            if item.room_id == room_id and item.start_date <= period_end and item.end_date >= period_start
        ]
        if candidates:
            return sorted(candidates, key=lambda item: item.start_date, reverse=True)[0]
        return ContractRepository.active_for_room(room_id)

    @staticmethod
    def _active_contracts_for_property_period(property_id: int, *, period_start, period_end):
        return [
            item
            for item in ContractRepository.list_active()
            if item.room.property_id == property_id and item.start_date <= period_end and item.end_date >= period_start
        ]

    @staticmethod
    def _calculate_reading_amount(*, bill: ElectricityBill, reading: ElectricityReading, total_usage: Decimal):
        contract = ElectricityService._resolve_contract_for_period(
            reading.room_id,
            period_start=bill.period_start,
            period_end=bill.period_end,
        )
        policy_code = UtilityPolicyResolver.resolve_electricity_policy(contract)
        usage = Decimal(str(reading.usage or 0))
        bill_total_amount = Decimal(str(bill.total_amount or 0))
        public_amount = Decimal(str(bill.public_amount or 0))
        breakdown = {
            "policy_code": policy_code,
            "usage": usage,
            "flow_amount": Decimal("0.00"),
            "public_amount": Decimal("0.00"),
            "total_amount": Decimal("0.00"),
        }

        if policy_code == UtilityPolicyResolver.FIXED_ELECTRICITY:
            rate = RatePolicyService.resolve_electricity_rate(contract)
            amount = (usage * rate).quantize(Decimal("0.01"))
            breakdown["flow_amount"] = amount
            breakdown["total_amount"] = amount
            return breakdown

        if total_usage <= 0:
            raise DomainValidationError("非固定電費策略需要有效的總用電度數才可計算")

        if policy_code == UtilityPolicyResolver.BILL_USAGE_RATIO:
            amount = (bill_total_amount * usage / total_usage).quantize(Decimal("0.01"))
            breakdown["flow_amount"] = amount
            breakdown["total_amount"] = amount
            return breakdown

        if policy_code == UtilityPolicyResolver.BILL_USAGE_RATIO_PLUS_PUBLIC:
            active_contracts = ElectricityService._active_contracts_for_property_period(
                bill.property_id,
                period_start=bill.period_start,
                period_end=bill.period_end,
            )
            active_room_count = len({item.room_id for item in active_contracts})
            if active_room_count <= 0:
                raise DomainValidationError("公電均攤策略需要至少一筆有效合約")

            flow_pool = bill_total_amount - public_amount
            flow_amount = (flow_pool * usage / total_usage).quantize(Decimal("0.01"))
            public_share = (public_amount / Decimal(active_room_count)).quantize(Decimal("0.01"))
            breakdown["flow_amount"] = flow_amount
            breakdown["public_amount"] = public_share
            breakdown["total_amount"] = (flow_amount + public_share).quantize(Decimal("0.01"))
            return breakdown

        raise DomainValidationError("未知的電費策略，無法計算")

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
        calculated_amount = payload.get("calculated_amount")
        if calculated_amount in (None, ""):
            contract = ElectricityService._resolve_contract_for_period(
                payload.get("room_id"),
                period_start=bill.period_start,
                period_end=bill.period_end,
            )
            policy_code = UtilityPolicyResolver.resolve_electricity_policy(contract)
            if policy_code == UtilityPolicyResolver.FIXED_ELECTRICITY:
                rate = RatePolicyService.resolve_electricity_rate(contract)
                calculated_amount = (usage * rate).quantize(Decimal("0.01"))
            else:
                calculated_amount = Decimal("0.00")
        payload["calculated_amount"] = calculated_amount
        if confirmed_amount is not None:
            payload["confirmed_amount"] = confirmed_amount

        reading = ElectricityReading(bill_id=bill.id, **payload)
        db.session.add(reading)
        db.session.commit()
        return reading

    @staticmethod
    def calculate_bill(bill: ElectricityBill):
        readings = ElectricityReadingRepository.list_for_bill(bill.id)
        total_usage = sum((Decimal(str(item.usage or 0)) for item in readings), Decimal("0.0"))
        flow_amount = Decimal("0.00")
        total_amount = Decimal("0.00")
        has_policy_resolver_amount = False

        for reading in readings:
            breakdown = ElectricityService._calculate_reading_amount(
                bill=bill,
                reading=reading,
                total_usage=total_usage,
            )
            reading.calculated_amount = breakdown["total_amount"]
            effective_amount = Decimal(
                str(reading.confirmed_amount if reading.confirmed_amount is not None else reading.calculated_amount or 0)
            )
            flow_amount += effective_amount
            total_amount += effective_amount
            if breakdown["policy_code"] != UtilityPolicyResolver.FIXED_ELECTRICITY:
                has_policy_resolver_amount = True

        bill.total_usage = total_usage
        bill.flow_amount = flow_amount.quantize(Decimal("0.01"))
        if has_policy_resolver_amount:
            bill.total_amount = total_amount.quantize(Decimal("0.01"))
        else:
            bill.total_amount = (bill.flow_amount + Decimal(str(bill.public_amount or 0))).quantize(Decimal("0.01"))
        bill.status = "calculated"
        db.session.commit()
        return bill

    @staticmethod
    def post_to_monthly_bill(*, monthly_bill: MonthlyBill, reading: ElectricityReading, public_electricity=0):
        bill = reading.bill
        resolved_public = Decimal(str(public_electricity or 0))
        electricity_amount = Decimal(str(reading.confirmed_amount or reading.calculated_amount or 0))
        if bill is not None:
            breakdown = ElectricityService._calculate_reading_amount(
                bill=bill,
                reading=reading,
                total_usage=Decimal(str(bill.total_usage or 0)),
            )
            if breakdown["policy_code"] == UtilityPolicyResolver.BILL_USAGE_RATIO_PLUS_PUBLIC and not public_electricity:
                resolved_public = breakdown["public_amount"]
                electricity_amount = breakdown["flow_amount"]

        monthly_bill.electricity_prev = reading.prev_reading
        monthly_bill.electricity_curr = reading.curr_reading
        monthly_bill.electricity_usage = reading.usage
        monthly_bill.electricity_amount = electricity_amount
        monthly_bill.public_electricity = resolved_public
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

    @staticmethod
    def property_overview(*, property_obj, meters, bills):
        total_public_amount = sum((Decimal(str(bill.public_amount or 0)) for bill in bills), Decimal("0.00"))
        total_flow_amount = sum((Decimal(str(bill.flow_amount or 0)) for bill in bills), Decimal("0.00"))
        total_bill_amount = sum((Decimal(str(bill.total_amount or 0)) for bill in bills), Decimal("0.00"))
        return {
            "property_id": property_obj.id,
            "property_name": property_obj.name,
            "meter_count": len(meters),
            "main_meter_count": sum(1 for meter in meters if meter.is_main),
            "bill_count": len(bills),
            "pending_count": sum(1 for bill in bills if bill.status == "pending"),
            "calculated_count": sum(1 for bill in bills if bill.status == "calculated"),
            "posted_count": sum(1 for bill in bills if bill.status == "posted"),
            "total_public_amount": total_public_amount,
            "total_flow_amount": total_flow_amount,
            "total_bill_amount": total_bill_amount,
        }
