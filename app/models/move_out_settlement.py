from decimal import Decimal

from app.core.db import db
from app.models.base import BaseModel


class MoveOutSettlement(BaseModel):
    __tablename__ = "move_out_settlements"

    CHARGE_FIELDS = (
        "final_rent", "electricity_amount", "water_amount", "management_fee",
        "previous_debt", "cleaning_fee", "repair_fee", "other_charge",
    )
    TRANSITIONS = {"draft": {"settled", "cancelled"}, "settled": {"voided"}, "voided": set(), "cancelled": set()}

    contract_id = db.Column(db.Integer, db.ForeignKey("contracts.id", ondelete="RESTRICT"), nullable=False, unique=True, index=True)
    final_monthly_bill_id = db.Column(db.Integer, db.ForeignKey("monthly_bills.id", ondelete="RESTRICT"), index=True)
    move_out_date = db.Column(db.Date, nullable=False, index=True)
    final_rent = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    electricity_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    water_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    management_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    previous_debt = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cleaning_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    repair_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    other_charge = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    other_desc = db.Column(db.String(200))
    deposit_held = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    refund_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    evidence_type = db.Column(db.String(20))
    evidence_reference = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), index=True)
    settled_at = db.Column(db.DateTime)
    voided_at = db.Column(db.DateTime)
    void_reason = db.Column(db.String(200))

    contract = db.relationship("Contract", backref=db.backref("move_out_settlement", uselist=False), lazy=True)
    final_monthly_bill = db.relationship("MonthlyBill", lazy=True)
    created_by = db.relationship("User", foreign_keys=[created_by_id], lazy=True)
    allocations = db.relationship("MoveOutSettlementAllocation", backref="settlement", lazy=True, cascade="all, delete-orphan")

    @property
    def gross_charges(self):
        return sum((Decimal(str(getattr(self, field) or 0)) for field in self.CHARGE_FIELDS), Decimal("0"))

    @property
    def allocated_amount(self):
        return sum((Decimal(str(item.amount or 0)) for item in self.allocations), Decimal("0"))

    @property
    def net_refund_amount(self):
        return max(Decimal(str(self.refund_amount or 0)) - self.allocated_amount, Decimal("0"))

    @property
    def outstanding_amount(self):
        return max(self.gross_charges - self.allocated_amount, Decimal("0"))


class MoveOutSettlementAllocation(BaseModel):
    __tablename__ = "move_out_settlement_allocations"

    settlement_id = db.Column(db.Integer, db.ForeignKey("move_out_settlements.id", ondelete="RESTRICT"), nullable=False, index=True)
    charge_type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    confirmed_by_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), index=True)

    confirmed_by = db.relationship("User", foreign_keys=[confirmed_by_id], lazy=True)
