from datetime import date

from app.core.year_month import to_db_year_month
from app.models import Contract, MonthlyBill
from app.repositories.billing_repository import BillingRepository
from app.repositories.room_repository import RoomRepository


class DashboardRepository:
    @staticmethod
    def build_summary(year_month: str | None = None):
        current_month = year_month or date.today().strftime("%Y-%m")
        db_year_month = to_db_year_month(current_month)
        return {
            "current_month": current_month,
            "current_month_db": db_year_month,
            "room_count": RoomRepository.count_all(),
            "occupied_count": RoomRepository.count_by_status("occupied"),
            "vacant_count": RoomRepository.count_by_status("vacant"),
            "month_collected": BillingRepository.sum_total_for_month(current_month, paid=True),
            "month_unpaid": BillingRepository.sum_total_for_month(current_month, paid=False),
            "active_contracts": ContractRepositoryShim.count_active(),
            "recent_bills": MonthlyBill.query.order_by(MonthlyBill.created_at.desc()).limit(10).all(),
        }


class ContractRepositoryShim:
    @staticmethod
    def count_active():
        return Contract.query.filter_by(status="active").count()
