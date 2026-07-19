from collections import OrderedDict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from app.core.year_month import to_db_year_month, to_ui_year_month
from app.repositories import PropertyRepository, ReportRepository


class ReportService:
    @staticmethod
    def _property_ids(property_ids):
        return sorted({int(property_id) for property_id in (property_ids or []) if int(property_id) > 0})

    @staticmethod
    def totals(rows, fields):
        return {field: sum((row.get(field) or 0) for row in rows) for field in fields}

    @staticmethod
    def _money(value):
        return Decimal(str(value or 0))

    @staticmethod
    def _outstanding_amount(total, paid_amount):
        return max(ReportService._money(total) - ReportService._money(paid_amount), Decimal("0"))

    @staticmethod
    def _month_bounds(year_month: str):
        db_year_month = to_db_year_month(year_month)
        year, month = int(db_year_month[:4]), int(db_year_month[4:])
        start_date = date(year, month, 1)
        end_date = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
        return start_date, end_date

    @staticmethod
    def export_money_rows(rows, money_fields):
        """Normalize exported money to the same whole-dollar rule used by the UI."""
        normalized = []
        for row in rows:
            exported = dict(row)
            for field in money_fields:
                exported[field] = int(
                    ReportService._money(exported.get(field)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                )
            normalized.append(exported)
        return normalized

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
                "public_electricity": row.public_electricity,
                "electricity_usage": row.electricity_usage,
                "water_amount": row.water_amount,
                "water_usage": row.water_usage,
                "other_charges": row.other_charges,
                "other_desc": row.other_desc,
                "previous_balance": row.previous_balance,
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

    @staticmethod
    def maintenance_summary(*, property_id=None, status=None, reported_from=None, reported_to=None):
        property_rows = ReportRepository.maintenance_property_summary_rows(
            property_id=property_id,
            status=status,
            reported_from=reported_from,
            reported_to=reported_to,
        )
        status_rows = ReportRepository.maintenance_status_summary_rows(
            property_id=property_id,
            status=status,
            reported_from=reported_from,
            reported_to=reported_to,
        )
        totals = {
            "request_count": sum((row.request_count or 0) for row in property_rows),
            "open_count": sum((row.open_count or 0) for row in property_rows),
            "estimated_total": sum((row.estimated_total or 0) for row in property_rows),
            "actual_total": sum((row.actual_total or 0) for row in property_rows),
        }
        return {
            "property_summary": property_rows,
            "status_summary": status_rows,
            "totals": totals,
        }

    @staticmethod
    def property_collection(year_month: str, property_ids=None):
        db_year_month = to_db_year_month(year_month)
        rows = ReportRepository.property_collection_rows(db_year_month, ReportService._property_ids(property_ids))
        result = []
        for row in rows:
            paid_amount = row.paid_amount or 0
            total = row.total or 0
            result.append(
                {
                    "year_month": to_ui_year_month(row.year_month),
                    "property_id": row.property_id,
                    "property_name": row.property_name,
                    "landlord_name": row.landlord_name,
                    "room_number": row.room_number,
                    "tenant_name": row.tenant_name,
                    "tenant_phone": row.tenant_phone,
                    "contract_start_date": row.contract_start_date,
                    "contract_end_date": row.contract_end_date,
                    "rent": row.rent or 0,
                    "electricity_amount": row.electricity_amount or 0,
                    "public_electricity": row.public_electricity or 0,
                    "water_amount": row.water_amount or 0,
                    "other_charges": row.other_charges or 0,
                    "other_desc": row.other_desc,
                    "previous_balance": row.previous_balance or 0,
                    "total": total,
                    "paid_amount": paid_amount,
                    "outstanding_amount": ReportService._outstanding_amount(total, paid_amount),
                }
            )
        return result

    @staticmethod
    def property_settlement(year_month: str, property_ids=None):
        db_year_month = to_db_year_month(year_month)
        rows = ReportRepository.property_settlement_rows(db_year_month, ReportService._property_ids(property_ids))
        selected_ids = ReportService._property_ids(property_ids)
        start_date, end_date = ReportService._month_bounds(year_month)
        expense_rows = ReportRepository.property_expense_summary_rows(start_date, end_date, selected_ids)
        expenses_by_property = {row.property_id: row for row in expense_rows}
        result = []
        for row in rows:
            expense_amount = (expenses_by_property.get(row.property_id).expense_amount or 0) if row.property_id in expenses_by_property else 0
            result.append(
                {
                "property_id": row.property_id,
                "property_name": row.property_name,
                "landlord_name": row.landlord_name,
                "bill_count": row.bill_count,
                "rent_amount": row.rent_amount or 0,
                "electricity_amount": row.electricity_amount or 0,
                "public_electricity": row.public_electricity or 0,
                "water_amount": row.water_amount or 0,
                "other_charges": row.other_charges or 0,
                "previous_balance": row.previous_balance or 0,
                "total_amount": row.total_amount or 0,
                "paid_amount": row.paid_amount or 0,
                "outstanding_amount": ReportService._outstanding_amount(row.total_amount, row.paid_amount),
                "expense_amount": expense_amount,
                "net_amount": ReportService._money(row.paid_amount) - ReportService._money(expense_amount),
                }
            )
        settled_property_ids = {row["property_id"] for row in result}
        for expense_row in expense_rows:
            if expense_row.property_id in settled_property_ids:
                continue
            expense_amount = expense_row.expense_amount or 0
            result.append(
                {
                    "property_id": expense_row.property_id,
                    "property_name": expense_row.property_name,
                    "landlord_name": expense_row.landlord_name,
                    "bill_count": 0,
                    "rent_amount": 0,
                    "electricity_amount": 0,
                    "public_electricity": 0,
                    "water_amount": 0,
                    "other_charges": 0,
                    "previous_balance": 0,
                    "total_amount": 0,
                    "paid_amount": 0,
                    "outstanding_amount": 0,
                    "expense_amount": expense_amount,
                    "net_amount": -ReportService._money(expense_amount),
                }
            )
        result.sort(key=lambda row: (row["landlord_name"], row["property_name"]))
        return result

    @staticmethod
    def property_expenses(year_month: str, property_ids=None):
        start_date, end_date = ReportService._month_bounds(year_month)
        rows = ReportRepository.property_expense_rows(
            start_date,
            end_date,
            ReportService._property_ids(property_ids),
        )
        return [
            {
                "transaction_date": row.transaction_date,
                "property_id": row.property_id,
                "property_name": row.property_name,
                "landlord_name": row.landlord_name,
                "category": row.category,
                "amount": row.amount or 0,
                "payee": row.payee,
                "reference_no": row.reference_no,
                "notes": row.notes,
            }
            for row in rows
        ]

    @staticmethod
    def new_tenants(year_month: str, property_ids=None):
        db_year_month = to_db_year_month(year_month)
        year, month = int(db_year_month[:4]), int(db_year_month[4:])
        start_date = date(year, month, 1)
        end_date = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
        rows = ReportRepository.new_tenant_rows(start_date, end_date, ReportService._property_ids(property_ids))
        return [
            {
                "property_id": row.property_id,
                "property_name": row.property_name,
                "room_number": row.room_number,
                "tenant_name": row.tenant_name,
                "tenant_phone": row.tenant_phone,
                "start_date": row.start_date,
                "end_date": row.end_date,
                "deposit": row.deposit or 0,
                "rent": row.rent or 0,
                "start_electricity_reading": row.start_electricity_reading,
                "start_water_reading": row.start_water_reading,
                "contract_status": row.contract_status,
                "notes": row.notes,
            }
            for row in rows
        ]

    @staticmethod
    def property_yearly(year: int, property_ids=None):
        selected_ids = ReportService._property_ids(property_ids)
        rows = ReportRepository.property_yearly_rows(year, selected_ids)
        by_property_month = {(row.property_id, row.year_month): row for row in rows}
        properties = [
            property_obj
            for property_obj in PropertyRepository.list_all()
            if not selected_ids or property_obj.id in selected_ids
        ]
        result = []
        for property_obj in properties:
            for month in range(1, 13):
                db_year_month = f"{year}{month:02d}"
                row = by_property_month.get((property_obj.id, db_year_month))
                total_amount = (row.total_amount or 0) if row else 0
                paid_amount = (row.paid_amount or 0) if row else 0
                result.append(
                    {
                        "year_month": to_ui_year_month(db_year_month),
                        "property_id": property_obj.id,
                        "property_name": property_obj.name,
                        "bill_count": row.bill_count if row else 0,
                        "rent_amount": (row.rent_amount or 0) if row else 0,
                        "electricity_amount": (row.electricity_amount or 0) if row else 0,
                        "public_electricity": (row.public_electricity or 0) if row else 0,
                        "water_amount": (row.water_amount or 0) if row else 0,
                        "other_charges": (row.other_charges or 0) if row else 0,
                        "previous_balance": (row.previous_balance or 0) if row else 0,
                        "total_amount": total_amount,
                        "paid_amount": paid_amount,
                        "outstanding_amount": ReportService._outstanding_amount(total_amount, paid_amount),
                    }
                )
        return result
