from decimal import Decimal

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
    total = db.Column(db.Numeric(10, 2), default=0)
    paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint("contract_id", "year_month", name="uq_monthly_bill_contract_year_month"),)

    @staticmethod
    def calculate_total(*, rent=0, electricity_amount=0, public_electricity=0, water_amount=0, other_charges=0):
        return (
            Decimal(str(rent or 0))
            + Decimal(str(electricity_amount or 0))
            + Decimal(str(public_electricity or 0))
            + Decimal(str(water_amount or 0))
            + Decimal(str(other_charges or 0))
        )


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
