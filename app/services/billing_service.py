from app.models import MonthlyBill


class BillingService:
    @staticmethod
    def calculate_total(monthly_bill: MonthlyBill):
        monthly_bill.total = MonthlyBill.calculate_total(
            rent=monthly_bill.rent,
            electricity_amount=monthly_bill.electricity_amount,
            public_electricity=monthly_bill.public_electricity,
            water_amount=monthly_bill.water_amount,
            other_charges=monthly_bill.other_charges,
        )
        return monthly_bill.total
