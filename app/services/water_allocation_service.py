from datetime import date
from decimal import Decimal

from app.core.errors import DomainValidationError
from app.models import Contract


class WaterAllocationService:
    @staticmethod
    def overlap_days(*, contract: Contract, billing_start: date, billing_end: date) -> int:
        start = max(contract.start_date, billing_start)
        end = min(contract.end_date, billing_end)
        if end < start:
            return 0
        return (end - start).days + 1

    @staticmethod
    def allocate_shared_by_stay_days(*, total_amount, contract_days: int, total_days: int):
        if total_days <= 0:
            raise DomainValidationError("總居住天數必須大於 0")
        if contract_days < 0:
            raise DomainValidationError("合約居住天數不可為負值")

        amount = Decimal(str(total_amount or 0)) * Decimal(contract_days) / Decimal(total_days)
        return amount.quantize(Decimal("0.01"))

    @staticmethod
    def allocate_independent_meter(*, amount):
        return Decimal(str(amount or 0)).quantize(Decimal("0.01"))
