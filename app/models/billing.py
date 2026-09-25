from decimal import Decimal, ROUND_HALF_UP

from app.core.db import db
from app.models.base import BaseModel


class MonthlyBill(BaseModel):
    __tablename__ = "monthly_bills"

    contract_id = db.Column(db.Integer, db.ForeignKey("contracts.id"), nullable=False)
    year_month = db.Column(db.String(6), nullable=False)
    rent = db.Column(db.Numeric(10, 2), default=0)
    electricity_prev = db.Column(db.Numeric(10, 1), default=0)
    electricity_curr = db.Column(db.Numeric(10, 1), default=0)
    electricity_usage = db.Column(db.Numeric(10, 1), default=0)
    electricity_amount = db.Column(db.Numeric(10, 2), default=0)
    public_electricity = db.Column(db.Numeric(10, 2), default=0)
    water_prev = db.Column(db.Numeric(10, 1), default=0)
    water_curr = db.Column(db.Numeric(10, 1), default=0)
    water_usage = db.Column(db.Numeric(10, 1), default=0)
    water_amount = db.Column(db.Numeric(10, 2), default=0)
    other_charges = db.Column(db.Numeric(10, 2), default=0)
    other_desc = db.Column(db.String(200))
    previous_balance = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), default=0)
    paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint("contract_id", "year_month", name="uq_monthly_bill_contract_year_month"),)

    @staticmethod
    def calculate_total(
        *, rent=0, electricity_amount=0, public_electricity=0, water_amount=0, other_charges=0, previous_balance=0
    ):
        total = (
            Decimal(str(rent or 0))
            + Decimal(str(electricity_amount or 0))
            + Decimal(str(public_electricity or 0))
            + Decimal(str(water_amount or 0))
            + Decimal(str(other_charges or 0))
            + Decimal(str(previous_balance or 0))
        )
        return total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


class PaymentRecord(BaseModel):
    __tablename__ = "payment_records"

    contract_id = db.Column(db.Integer, db.ForeignKey("contracts.id"), nullable=True)
    monthly_bill_id = db.Column(db.Integer, db.ForeignKey("monthly_bills.id"), nullable=True)
    amount = db.Column(db.Numeric(10, 2))
    bank_name = db.Column(db.String(50))
    account_number = db.Column(db.String(50))
    account_holder = db.Column(db.String(50))
    transaction_date = db.Column(db.Date)
    payer_name = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    status_text = db.Column(db.String(20))
    raw_ocr_text = db.Column(db.Text)
    raw_llm_response = db.Column(db.Text)
    image_path = db.Column(db.String(500))
    ocr_engine = db.Column(db.String(20))
    record_status = db.Column(db.String(20), default="pending")
    verified_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    verified_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    monthly_bill = db.relationship("MonthlyBill", backref="payment_records", lazy=True)
    verified_by = db.relationship("User", foreign_keys=[verified_by_id], lazy=True)


class WaterBill(BaseModel):
    __tablename__ = "water_bills"

    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    billing_start = db.Column(db.Date, nullable=False)
    billing_end = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    meter_prev_1 = db.Column(db.Numeric(10, 1), default=0)
    meter_curr_1 = db.Column(db.Numeric(10, 1), default=0)
    sub_meter_1 = db.Column(db.Numeric(10, 1), default=0)
    actual_usage_1 = db.Column(db.Numeric(10, 1), default=0)
    meter_prev_2 = db.Column(db.Numeric(10, 1), default=0)
    meter_curr_2 = db.Column(db.Numeric(10, 1), default=0)
    sub_meter_2 = db.Column(db.Numeric(10, 1), default=0)
    actual_usage_2 = db.Column(db.Numeric(10, 1), default=0)
    notes = db.Column(db.Text)

    property = db.relationship("Property", backref="water_bills", lazy=True)


class UtilityCalculationDraft(BaseModel):
    __tablename__ = "utility_calculation_drafts"

    DRAFT = "draft"
    CONFIRMED = "confirmed"
    POSTED = "posted"

    utility_type = db.Column(db.String(20), nullable=False, index=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False, index=True)
    water_bill_id = db.Column(db.Integer, db.ForeignKey("water_bills.id"), nullable=True, index=True)
    electricity_bill_id = db.Column(db.Integer, db.ForeignKey("electricity_bills.id"), nullable=True, index=True)
    year_month = db.Column(db.String(6), nullable=False, index=True)
    billing_start = db.Column(db.Date, nullable=False)
    billing_end = db.Column(db.Date, nullable=False)
    policy_code = db.Column(db.String(50), nullable=False)
    rounding_mode = db.Column(db.String(40), nullable=False)
    billed_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    allocated_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    reconciliation_difference = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default=DRAFT, index=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    posted_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, default="")

    __table_args__ = (
        db.CheckConstraint(
            "(water_bill_id IS NOT NULL AND electricity_bill_id IS NULL) "
            "OR (water_bill_id IS NULL AND electricity_bill_id IS NOT NULL)",
            name="ck_utility_draft_has_exactly_one_source_bill",
        ),
    )

    property = db.relationship("Property", backref="utility_calculation_drafts", lazy=True)
    water_bill = db.relationship("WaterBill", backref="calculation_drafts", lazy=True)
    electricity_bill = db.relationship("ElectricityBill", backref="calculation_drafts", lazy=True)


class UtilityCalculationLine(BaseModel):
    __tablename__ = "utility_calculation_lines"

    draft_id = db.Column(
        db.Integer,
        db.ForeignKey("utility_calculation_drafts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=True, index=True)
    contract_id = db.Column(db.Integer, db.ForeignKey("contracts.id"), nullable=True, index=True)
    monthly_bill_id = db.Column(db.Integer, db.ForeignKey("monthly_bills.id"), nullable=True, index=True)
    room_number_snapshot = db.Column(db.String(20), nullable=False)
    occupant_name_snapshot = db.Column(db.String(100), nullable=True)
    occupancy_status = db.Column(db.String(20), nullable=False)
    exclusion_reason = db.Column(db.String(200), nullable=True)
    stay_days = db.Column(db.Integer, nullable=False, default=0)
    calculated_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    confirmed_amount = db.Column(db.Numeric(10, 2), nullable=True)

    draft = db.relationship(
        "UtilityCalculationDraft",
        backref=db.backref("lines", lazy=True, cascade="all, delete-orphan", order_by="UtilityCalculationLine.id"),
    )
    room = db.relationship("Room", lazy=True)
    contract = db.relationship("Contract", lazy=True)
    monthly_bill = db.relationship("MonthlyBill", lazy=True)
