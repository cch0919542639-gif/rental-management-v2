from sqlalchemy import case, func

from app.core.db import db
from app.models import Contract, Landlord, MonthlyBill, Property, Room, Tenant


class ReportRepository:
    @staticmethod
    def monthly_report_rows(year_month: str):
        return (
            db.session.query(
                MonthlyBill.year_month.label("year_month"),
                Landlord.name.label("landlord_name"),
                Property.name.label("property_name"),
                Room.room_number.label("room_number"),
                Tenant.name.label("tenant_name"),
                MonthlyBill.rent.label("rent"),
                MonthlyBill.electricity_amount.label("electricity_amount"),
                MonthlyBill.electricity_usage.label("electricity_usage"),
                MonthlyBill.water_amount.label("water_amount"),
                MonthlyBill.water_usage.label("water_usage"),
                MonthlyBill.other_charges.label("other_charges"),
                MonthlyBill.total.label("total"),
                MonthlyBill.paid.label("paid"),
            )
            .join(Contract, Contract.id == MonthlyBill.contract_id)
            .join(Room, Room.id == Contract.room_id)
            .join(Property, Property.id == Room.property_id)
            .join(Landlord, Landlord.id == Property.landlord_id)
            .join(Tenant, Tenant.id == Contract.tenant_id)
            .filter(MonthlyBill.year_month == year_month)
            .order_by(Landlord.name.asc(), Property.name.asc(), Room.room_number.asc())
            .all()
        )

    @staticmethod
    def landlord_summary_rows(year_month: str):
        return (
            db.session.query(
                Landlord.id.label("landlord_id"),
                Landlord.name.label("landlord_name"),
                Property.id.label("property_id"),
                Property.name.label("property_name"),
                func.count(MonthlyBill.id).label("bill_count"),
                func.sum(MonthlyBill.total).label("total_amount"),
                func.sum(case((MonthlyBill.paid.is_(True), MonthlyBill.total), else_=0)).label("paid_amount"),
                func.sum(case((MonthlyBill.paid.is_(False), MonthlyBill.total), else_=0)).label("unpaid_amount"),
            )
            .join(Room, Room.property_id == Property.id)
            .join(Contract, Contract.room_id == Room.id)
            .join(MonthlyBill, MonthlyBill.contract_id == Contract.id)
            .join(Landlord, Landlord.id == Property.landlord_id)
            .filter(MonthlyBill.year_month == year_month)
            .group_by(Landlord.id, Landlord.name, Property.id, Property.name)
            .order_by(Landlord.name.asc(), Property.name.asc())
            .all()
        )

    @staticmethod
    def yearly_overview_rows(year: int):
        return (
            db.session.query(
                MonthlyBill.year_month.label("year_month"),
                func.sum(MonthlyBill.total).label("total_amount"),
                func.sum(case((MonthlyBill.paid.is_(True), MonthlyBill.total), else_=0)).label("paid_amount"),
                func.sum(case((MonthlyBill.paid.is_(False), MonthlyBill.total), else_=0)).label("unpaid_amount"),
            )
            .filter(MonthlyBill.year_month.like(f"{year}%"))
            .group_by(MonthlyBill.year_month)
            .order_by(MonthlyBill.year_month.asc())
            .all()
        )
