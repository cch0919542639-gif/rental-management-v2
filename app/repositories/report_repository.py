from sqlalchemy import case, func

from app.core.db import db
from app.models import Contract, Landlord, MonthlyBill, Property, Room, Tenant
from app.models.maintenance import MaintenanceRequest


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
                MonthlyBill.other_desc.label("other_desc"),
                MonthlyBill.public_electricity.label("public_electricity"),
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

    @staticmethod
    def maintenance_property_summary_rows(*, property_id=None, status=None, reported_from=None, reported_to=None):
        query = (
            db.session.query(
                Landlord.name.label("landlord_name"),
                Property.name.label("property_name"),
                func.count(MaintenanceRequest.id).label("request_count"),
                func.sum(
                    case((MaintenanceRequest.status.in_(["reported", "assigned", "in_progress"]), 1), else_=0)
                ).label("open_count"),
                func.coalesce(func.sum(MaintenanceRequest.estimated_cost), 0).label("estimated_total"),
                func.coalesce(func.sum(MaintenanceRequest.actual_cost), 0).label("actual_total"),
            )
            .join(Room, Room.property_id == Property.id)
            .join(MaintenanceRequest, MaintenanceRequest.room_id == Room.id)
            .join(Landlord, Landlord.id == Property.landlord_id)
        )
        if property_id:
            query = query.filter(Property.id == property_id)
        if status:
            query = query.filter(MaintenanceRequest.status == status)
        if reported_from:
            query = query.filter(func.date(MaintenanceRequest.reported_at) >= reported_from)
        if reported_to:
            query = query.filter(func.date(MaintenanceRequest.reported_at) <= reported_to)
        return (
            query.group_by(Landlord.name, Property.name)
            .order_by(Landlord.name.asc(), Property.name.asc())
            .all()
        )

    @staticmethod
    def maintenance_status_summary_rows(*, property_id=None, status=None, reported_from=None, reported_to=None):
        query = (
            db.session.query(
                MaintenanceRequest.status.label("status"),
                func.count(MaintenanceRequest.id).label("request_count"),
                func.coalesce(func.sum(MaintenanceRequest.estimated_cost), 0).label("estimated_total"),
                func.coalesce(func.sum(MaintenanceRequest.actual_cost), 0).label("actual_total"),
            )
            .join(Room, Room.id == MaintenanceRequest.room_id)
            .join(Property, Property.id == Room.property_id)
        )
        if property_id:
            query = query.filter(Property.id == property_id)
        if status:
            query = query.filter(MaintenanceRequest.status == status)
        if reported_from:
            query = query.filter(func.date(MaintenanceRequest.reported_at) >= reported_from)
        if reported_to:
            query = query.filter(func.date(MaintenanceRequest.reported_at) <= reported_to)
        return (
            query.group_by(MaintenanceRequest.status)
            .order_by(MaintenanceRequest.status.asc())
            .all()
        )
