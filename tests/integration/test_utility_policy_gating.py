from decimal import Decimal

import pytest

from app.core.errors import DomainValidationError
from app.models import Contract
from app.services import RatePolicyService, UtilityPolicyResolver


def test_rate_policy_service_allows_fixed_rate_fallback(app, seeded_data):
    with app.app_context():
        contract = app.extensions["sqlalchemy"].session.get(Contract, seeded_data["contract_id"])
        contract.room.property.electricity_policy_code = UtilityPolicyResolver.FIXED_ELECTRICITY
        contract.room.property.water_policy_code = UtilityPolicyResolver.WATER_FREE

        assert RatePolicyService.resolve_electricity_rate(contract) == Decimal("5.00")
        assert RatePolicyService.resolve_water_rate(contract) == Decimal("0.00")


def test_rate_policy_service_blocks_non_fixed_electricity_policy(app, seeded_data):
    with app.app_context():
        contract = app.extensions["sqlalchemy"].session.get(Contract, seeded_data["contract_id"])
        contract.room.property.electricity_policy_code = UtilityPolicyResolver.BILL_USAGE_RATIO

        with pytest.raises(DomainValidationError):
            RatePolicyService.resolve_electricity_rate(contract)


def test_rate_policy_service_blocks_non_fixed_water_policy(app, seeded_data):
    with app.app_context():
        contract = app.extensions["sqlalchemy"].session.get(Contract, seeded_data["contract_id"])
        contract.room.property.water_policy_code = UtilityPolicyResolver.WATER_BILL_BY_STAY_DAYS

        with pytest.raises(DomainValidationError):
            RatePolicyService.resolve_water_rate(contract)
