from sqlalchemy import case, func

from app.core.db import db
from app.models import (
    Contract, Landlord, MonthlyBill, MoveOutSettlement, MoveOutSettlementAllocation,
    PaymentRecord, Property, PropertyExpense, Room, Tenant,
)
from app.models.maintenance import MaintenanceRequest


class ReportRepository:
    @staticmethod
    def _paid_expr():
        return func.coalesce(MonthlyBill.paid, False)

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
                MonthlyBill.previous_balance.label("previous_balance"),
                MonthlyBill.total.label("total"),
                func.coalesce(MonthlyBill.paid, False).label("paid"),
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
                func.sum(case((ReportRepository._paid_expr().is_(True), MonthlyBill.total), else_=0)).label("paid_amount"),
                func.sum(case((ReportRepository._paid_expr().is_(False), MonthlyBill.total), else_=0)).label("unpaid_amount"),
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
                func.sum(case((ReportRepository._paid_expr().is_(True), MonthlyBill.total), else_=0)).label("paid_amount"),
                func.sum(case((ReportRepository._paid_expr().is_(False), MonthlyBill.total), else_=0)).label("unpaid_amount"),
            )
            .filter(MonthlyBill.year_month.like(f"{year}%"))
            .group_by(MonthlyBill.year_month)
            .order_by(MonthlyBill.year_month.asc())
            .all()
        )

    @staticmethod
    def _linked_payment_amounts():
        return (
            db.session.query(
                PaymentRecord.monthly_bill_id.label("monthly_bill_id"),
                func.coalesce(func.sum(PaymentRecord.amount), 0).label("paid_amount"),
            )
            .filter(
                PaymentRecord.record_status == "linked",
                PaymentRecord.monthly_bill_id.isnot(None),
            )
            .group_by(PaymentRecord.monthly_bill_id)
            .subquery()
        )

    @staticmethod
    def property_collection_rows(year_month: str, property_ids: list[int] | None = None):
        linked_payments = ReportRepository._linked_payment_amounts()
        query = (
            db.session.query(
                MonthlyBill.year_month.label("year_month"),
                Property.id.label("property_id"),
                Property.name.label("property_name"),
                Landlord.name.label("landlord_name"),
                Room.room_number.label("room_number"),
                Tenant.name.label("tenant_name"),
                Tenant.phone.label("tenant_phone"),
                Contract.start_date.label("contract_start_date"),
                Contract.end_date.label("contract_end_date"),
                MonthlyBill.rent.label("rent"),
                MonthlyBill.electricity_amount.label("electricity_amount"),
                MonthlyBill.public_electricity.label("public_electricity"),
                MonthlyBill.water_amount.label("water_amount"),
                MonthlyBill.other_charges.label("other_charges"),
                MonthlyBill.other_desc.label("other_desc"),
                MonthlyBill.previous_balance.label("previous_balance"),
                MonthlyBill.total.label("total"),
                func.coalesce(linked_payments.c.paid_amount, 0).label("paid_amount"),
            )
            .join(Contract, Contract.id == MonthlyBill.contract_id)
            .join(Room, Room.id == Contract.room_id)
            .join(Property, Property.id == Room.property_id)
            .join(Landlord, Landlord.id == Property.landlord_id)
            .join(Tenant, Tenant.id == Contract.tenant_id)
            .outerjoin(linked_payments, linked_payments.c.monthly_bill_id == MonthlyBill.id)
            .filter(MonthlyBill.year_month == year_month)
        )
        if property_ids:
            query = query.filter(Property.id.in_(property_ids))
        return query.order_by(Property.name.asc(), Room.room_number.asc(), Tenant.name.asc()).all()

    @staticmethod
    def property_settlement_rows(year_month: str, property_ids: list[int] | None = None):
        linked_payments = ReportRepository._linked_payment_amounts()
        query = (
            db.session.query(
                Property.id.label("property_id"),
                Property.name.label("property_name"),
                Landlord.name.label("landlord_name"),
                func.count(MonthlyBill.id).label("bill_count"),
                func.coalesce(func.sum(MonthlyBill.rent), 0).label("rent_amount"),
                func.coalesce(func.sum(MonthlyBill.electricity_amount), 0).label("electricity_amount"),
                func.coalesce(func.sum(MonthlyBill.public_electricity), 0).label("public_electricity"),
                func.coalesce(func.sum(MonthlyBill.water_amount), 0).label("water_amount"),
                func.coalesce(func.sum(MonthlyBill.other_charges), 0).label("other_charges"),
                func.coalesce(func.sum(MonthlyBill.previous_balance), 0).label("previous_balance"),
                func.coalesce(func.sum(MonthlyBill.total), 0).label("total_amount"),
                func.coalesce(func.sum(linked_payments.c.paid_amount), 0).label("paid_amount"),
            )
            .join(Contract, Contract.id == MonthlyBill.contract_id)
            .join(Room, Room.id == Contract.room_id)
            .join(Property, Property.id == Room.property_id)
            .join(Landlord, Landlord.id == Property.landlord_id)
            .outerjoin(linked_payments, linked_payments.c.monthly_bill_id == MonthlyBill.id)
            .filter(MonthlyBill.year_month == year_month)
        )
        if property_ids:
            query = query.filter(Property.id.in_(property_ids))
        return (
            query.group_by(Property.id, Property.name, Landlord.name)
            .order_by(Landlord.name.asc(), Property.name.asc())
            .all()
        )

    @staticmethod
    def property_expense_rows(start_date, end_date, property_ids: list[int] | None = None):
        query = (
            db.session.query(
                PropertyExpense.transaction_date.label("transaction_date"),
                Property.id.label("property_id"),
                Property.name.label("property_name"),
                Landlord.name.label("landlord_name"),
                PropertyExpense.category.label("category"),
                PropertyExpense.amount.label("amount"),
                PropertyExpense.payee.label("payee"),
                PropertyExpense.reference_no.label("reference_no"),
                PropertyExpense.notes.label("notes"),
            )
            .join(Property, Property.id == PropertyExpense.property_id)
            .join(Landlord, Landlord.id == Property.landlord_id)
            .filter(
                PropertyExpense.record_status == "posted",
                PropertyExpense.transaction_date >= start_date,
                PropertyExpense.transaction_date < end_date,
            )
        )
        if property_ids:
            query = query.filter(Property.id.in_(property_ids))
        return query.order_by(
            PropertyExpense.transaction_date.asc(),
            Landlord.name.asc(),
            Property.name.asc(),
            PropertyExpense.id.asc(),
        ).all()

    @staticmethod
    def property_expense_summary_rows(start_date, end_date, property_ids: list[int] | None = None):
        query = (
            db.session.query(
                PropertyExpense.property_id.label("property_id"),
                Property.name.label("property_name"),
                Landlord.name.label("landlord_name"),
                func.coalesce(func.sum(PropertyExpense.amount), 0).label("expense_amount"),
            )
            .join(Property, Property.id == PropertyExpense.property_id)
            .join(Landlord, Landlord.id == Property.landlord_id)
            .filter(
                PropertyExpense.record_status == "posted",
                PropertyExpense.transaction_date >= start_date,
                PropertyExpense.transaction_date < end_date,
            )
        )
        if property_ids:
            query = query.filter(PropertyExpense.property_id.in_(property_ids))
        return query.group_by(PropertyExpense.property_id, Property.name, Landlord.name).all()

    @staticmethod
    def move_out_settlement_rows(start_date, end_date, property_ids: list[int] | None = None, status: str | None = None):
        allocations = (
            db.session.query(
                MoveOutSettlementAllocation.settlement_id.label("settlement_id"),
                func.coalesce(func.sum(MoveOutSettlementAllocation.amount), 0).label("allocated_amount"),
            )
            .group_by(MoveOutSettlementAllocation.settlement_id)
            .subquery()
        )
        query = (
            db.session.query(
                MoveOutSettlement.id.label("settlement_id"),
                MoveOutSettlement.move_out_date.label("move_out_date"),
                MoveOutSettlement.status.label("status"),
                Landlord.name.label("landlord_name"),
                Property.id.label("property_id"),
                Property.name.label("property_name"),
                Room.room_number.label("room_number"),
                Tenant.name.label("tenant_name"),
                Tenant.phone.label("tenant_phone"),
                MoveOutSettlement.deposit_held.label("deposit_held"),
                MoveOutSettlement.refund_amount.label("refund_amount"),
                MoveOutSettlement.final_rent.label("final_rent"),
                MoveOutSettlement.electricity_amount.label("electricity_amount"),
                MoveOutSettlement.water_amount.label("water_amount"),
                MoveOutSettlement.management_fee.label("management_fee"),
                MoveOutSettlement.previous_debt.label("previous_debt"),
                MoveOutSettlement.cleaning_fee.label("cleaning_fee"),
                MoveOutSettlement.repair_fee.label("repair_fee"),
                MoveOutSettlement.other_charge.label("other_charge"),
                MoveOutSettlement.other_desc.label("other_desc"),
                MoveOutSettlement.evidence_type.label("evidence_type"),
                MoveOutSettlement.evidence_reference.label("evidence_reference"),
                func.coalesce(allocations.c.allocated_amount, 0).label("allocated_amount"),
            )
            .join(Contract, Contract.id == MoveOutSettlement.contract_id)
            .join(Room, Room.id == Contract.room_id)
            .join(Property, Property.id == Room.property_id)
            .join(Landlord, Landlord.id == Property.landlord_id)
            .join(Tenant, Tenant.id == Contract.tenant_id)
            .outerjoin(allocations, allocations.c.settlement_id == MoveOutSettlement.id)
            .filter(MoveOutSettlement.move_out_date >= start_date, MoveOutSettlement.move_out_date < end_date)
        )
        if property_ids:
            query = query.filter(Property.id.in_(property_ids))
        if status == "unsettled":
            query = query.filter(MoveOutSettlement.status != "settled")
        elif status:
            query = query.filter(MoveOutSettlement.status == status)
        return query.order_by(MoveOutSettlement.move_out_date.asc(), Property.name.asc(), Room.room_number.asc()).all()

    @staticmethod
    def new_tenant_rows(start_date, end_date, property_ids: list[int] | None = None):
        query = (
            db.session.query(
                Property.id.label("property_id"),
                Property.name.label("property_name"),
                Room.room_number.label("room_number"),
                Tenant.name.label("tenant_name"),
                Tenant.phone.label("tenant_phone"),
                Contract.start_date.label("start_date"),
                Contract.end_date.label("end_date"),
                Contract.deposit.label("deposit"),
                Contract.rent.label("rent"),
                Contract.start_electricity_reading.label("start_electricity_reading"),
                Contract.start_water_reading.label("start_water_reading"),
                Contract.status.label("contract_status"),
                Contract.notes.label("notes"),
            )
            .join(Room, Room.id == Contract.room_id)
            .join(Property, Property.id == Room.property_id)
            .join(Tenant, Tenant.id == Contract.tenant_id)
            .filter(Contract.start_date >= start_date, Contract.start_date < end_date)
        )
        if property_ids:
            query = query.filter(Property.id.in_(property_ids))
        return query.order_by(Property.name.asc(), Room.room_number.asc(), Tenant.name.asc()).all()

    @staticmethod
    def property_yearly_rows(year: int, property_ids: list[int] | None = None):
        linked_payments = ReportRepository._linked_payment_amounts()
        query = (
            db.session.query(
                MonthlyBill.year_month.label("year_month"),
                Property.id.label("property_id"),
                Property.name.label("property_name"),
                func.count(MonthlyBill.id).label("bill_count"),
                func.coalesce(func.sum(MonthlyBill.rent), 0).label("rent_amount"),
                func.coalesce(func.sum(MonthlyBill.electricity_amount), 0).label("electricity_amount"),
                func.coalesce(func.sum(MonthlyBill.public_electricity), 0).label("public_electricity"),
                func.coalesce(func.sum(MonthlyBill.water_amount), 0).label("water_amount"),
                func.coalesce(func.sum(MonthlyBill.other_charges), 0).label("other_charges"),
                func.coalesce(func.sum(MonthlyBill.previous_balance), 0).label("previous_balance"),
                func.coalesce(func.sum(MonthlyBill.total), 0).label("total_amount"),
                func.coalesce(func.sum(linked_payments.c.paid_amount), 0).label("paid_amount"),
            )
            .join(Contract, Contract.id == MonthlyBill.contract_id)
            .join(Room, Room.id == Contract.room_id)
            .join(Property, Property.id == Room.property_id)
            .outerjoin(linked_payments, linked_payments.c.monthly_bill_id == MonthlyBill.id)
            .filter(MonthlyBill.year_month.like(f"{year}%"))
        )
        if property_ids:
            query = query.filter(Property.id.in_(property_ids))
        return (
            query.group_by(MonthlyBill.year_month, Property.id, Property.name)
            .order_by(MonthlyBill.year_month.asc(), Property.name.asc())
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
