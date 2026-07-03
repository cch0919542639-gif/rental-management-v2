from decimal import Decimal

from app.core.errors import DomainValidationError
from app.models import Contract
from app.services.utility_policy_resolver import UtilityPolicyResolver


class RatePolicyService:
    @staticmethod
    def resolve_electricity_rate(contract: Contract | None):
        if contract is None:
            return Decimal("0.00")
        policy_code = UtilityPolicyResolver.resolve_electricity_policy(contract)
        if policy_code != UtilityPolicyResolver.FIXED_ELECTRICITY:
            raise DomainValidationError(
                "此物件的電費策略不是固定單價，需先完成 utility policy resolver 流程後才可自動計算。"
            )
        if contract.electricity_rate is not None:
            return Decimal(str(contract.electricity_rate))
        landlord_rate = contract.room.property.landlord.electricity_rate
        return Decimal(str(landlord_rate or 0)).quantize(Decimal("0.00"))

    @staticmethod
    def resolve_water_rate(contract: Contract | None):
        if contract is None:
            return Decimal("0.00")
        policy_code = UtilityPolicyResolver.resolve_water_policy(contract)
        if policy_code == UtilityPolicyResolver.WATER_FREE:
            return Decimal("0.00")
        if policy_code != UtilityPolicyResolver.WATER_FIXED_MONTHLY:
            raise DomainValidationError(
                "此物件的水費策略不是固定月費，需先完成 utility policy resolver 流程後才可自動取固定值。"
            )
        if contract.water_rate is not None:
            return Decimal(str(contract.water_rate))
        landlord_rate = contract.room.property.landlord.water_rate
        return Decimal(str(landlord_rate or 0)).quantize(Decimal("0.00"))
