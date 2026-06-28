from decimal import Decimal


class PaymentReconciliationService:
    @staticmethod
    def is_bill_paid(*, bill_total, paid_amount):
        return Decimal(str(paid_amount or 0)) >= Decimal(str(bill_total or 0))
