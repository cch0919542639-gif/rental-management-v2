from collections import OrderedDict

from app.core.year_month import to_db_year_month, to_ui_year_month
from app.repositories import ReportRepository


class ReportService:
    @staticmethod
    def monthly_report(year_month: str):
        db_year_month = to_db_year_month(year_month)
        rows = ReportRepository.monthly_report_rows(db_year_month)
        return [
            {
                "year_month": to_ui_year_month(row.year_month),
                "landlord_name": row.landlord_name,
                "property_name": row.property_name,
                "room_number": row.room_number,
                "tenant_name": row.tenant_name,
                "rent": row.rent,
                "electricity_amount": row.electricity_amount,
                "electricity_usage": row.electricity_usage,
                "water_amount": row.water_amount,
                "water_usage": row.water_usage,
                "other_charges": row.other_charges,
                "total": row.total,
                "paid": row.paid,
            }
            for row in rows
        ]

    @staticmethod
    def landlord_summary(year_month: str):
        db_year_month = to_db_year_month(year_month)
        rows = ReportRepository.landlord_summary_rows(db_year_month)
        return [
            {
                "landlord_id": row.landlord_id,
                "landlord_name": row.landlord_name,
                "property_id": row.property_id,
                "property_name": row.property_name,
                "bill_count": row.bill_count,
                "total_amount": row.total_amount or 0,
                "paid_amount": row.paid_amount or 0,
                "unpaid_amount": row.unpaid_amount or 0,
            }
            for row in rows
        ]

    @staticmethod
    def yearly_overview(year: int):
        rows = ReportRepository.yearly_overview_rows(year)
        result = OrderedDict()
        for month in range(1, 13):
            key = f"{year}-{month:02d}"
            result[key] = {
                "year_month": key,
                "total_amount": 0,
                "paid_amount": 0,
                "unpaid_amount": 0,
            }
        for row in rows:
            key = to_ui_year_month(row.year_month)
            result[key] = {
                "year_month": key,
                "total_amount": row.total_amount or 0,
                "paid_amount": row.paid_amount or 0,
                "unpaid_amount": row.unpaid_amount or 0,
            }
        return list(result.values())
