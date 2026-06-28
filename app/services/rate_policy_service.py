from decimal import Decimal

from app.models import Contract


class RatePolicyService:
    @staticmethod
    def resolve_electricity_rate(contract: Contract | None):
        if contract is None:
            return Decimal("0.00")
        if contract.electricity_rate is not None:
            return Decimal(str(contract.electricity_rate))
        landlord_rate = contract.room.property.landlord.electricity_rate
        return Decimal(str(landlord_rate or 0)).quantize(Decimal("0.00"))

    @staticmethod
    def resolve_water_rate(contract: Contract | None):
        if contract is None:
            return Decimal("0.00")
        if contract.water_rate is not None:
            return Decimal(str(contract.water_rate))
        landlord_rate = contract.room.property.landlord.water_rate
        return Decimal(str(landlord_rate or 0)).quantize(Decimal("0.00"))
