from app.models import Contract


class UtilityPolicyResolver:
    FIXED_ELECTRICITY = "electricity_fixed_rate"
    BILL_USAGE_RATIO = "electricity_bill_usage_ratio"
    BILL_USAGE_RATIO_PLUS_PUBLIC = "electricity_bill_usage_ratio_plus_public_share"

    WATER_FIXED_MONTHLY = "water_fixed_monthly"
    WATER_FREE = "water_free"
    WATER_BILL_BY_STAY_DAYS = "water_bill_by_stay_days"

    ELECTRICITY_POLICY_CHOICES = [
        ("", "沿用既有固定費率"),
        (FIXED_ELECTRICITY, "固定每度單價"),
        (BILL_USAGE_RATIO, "整期按度數比例分攤"),
        (BILL_USAGE_RATIO_PLUS_PUBLIC, "公電均攤 + 度數分攤"),
    ]

    WATER_POLICY_CHOICES = [
        ("", "沿用既有預設"),
        (WATER_FIXED_MONTHLY, "固定月費"),
        (WATER_FREE, "不收水費"),
        (WATER_BILL_BY_STAY_DAYS, "按居住天數分攤"),
    ]

    @staticmethod
    def resolve_electricity_policy(contract: Contract | None):
        if contract is None:
            return UtilityPolicyResolver.FIXED_ELECTRICITY

        room = contract.room
        prop = room.property if room else None

        if getattr(room, "electricity_policy_code", None):
            return room.electricity_policy_code
        if getattr(prop, "electricity_policy_code", None):
            return prop.electricity_policy_code

        # Backward-compatible fallback for pre-policy rows.
        return UtilityPolicyResolver.FIXED_ELECTRICITY

    @staticmethod
    def resolve_water_policy(contract: Contract | None):
        if contract is None:
            return UtilityPolicyResolver.WATER_FREE

        room = contract.room
        prop = room.property if room else None

        if getattr(room, "water_policy_code", None):
            return room.water_policy_code
        if getattr(prop, "water_policy_code", None):
            return prop.water_policy_code

        landlord = prop.landlord if prop else None
        if landlord and getattr(landlord, "water_rate_type", None) == "fixed":
            amount = landlord.water_rate or 0
            if amount == 0:
                return UtilityPolicyResolver.WATER_FREE
            return UtilityPolicyResolver.WATER_FIXED_MONTHLY

        return UtilityPolicyResolver.WATER_FREE
