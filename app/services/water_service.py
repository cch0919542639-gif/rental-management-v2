class WaterService:
    @staticmethod
    def validate_billing_period(*, billing_start, billing_end):
        return billing_end > billing_start
