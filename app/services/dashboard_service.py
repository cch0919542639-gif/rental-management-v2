from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    @staticmethod
    def get_summary(year_month: str | None = None):
        return DashboardRepository.build_summary(year_month)
