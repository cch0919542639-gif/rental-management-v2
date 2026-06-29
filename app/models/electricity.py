from app.core.db import db
from app.models.base import BaseModel


class CalcMethod(BaseModel):
    __tablename__ = "calc_methods"

    name = db.Column(db.String(100), nullable=False)
    module_key = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    params_schema = db.Column(db.Text, default="{}")
    is_active = db.Column(db.Boolean, default=True)


class ElectricityMeter(BaseModel):
    __tablename__ = "electricity_meters"

    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    meter_number = db.Column(db.String(50))
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=True)
    room_number = db.Column(db.String(20))
    notes = db.Column(db.Text, default="")

    property = db.relationship("Property", backref="electricity_meters", lazy=True)
    room = db.relationship("Room", backref="electricity_meters", lazy=True)


class ElectricityBill(BaseModel):
    __tablename__ = "electricity_bills"

    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    meter_id = db.Column(db.Integer, db.ForeignKey("electricity_meters.id"), nullable=True)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    year_month = db.Column(db.String(6))
    prev_reading = db.Column(db.Numeric(10, 1), default=0)
    curr_reading = db.Column(db.Numeric(10, 1), default=0)
    total_usage = db.Column(db.Numeric(10, 1), default=0)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    public_amount = db.Column(db.Numeric(10, 2), default=0)
    flow_amount = db.Column(db.Numeric(10, 2), default=0)
    calc_method_id = db.Column(db.Integer, db.ForeignKey("calc_methods.id"))
    status = db.Column(db.String(20), default="pending")
    ocr_raw_text = db.Column(db.Text)
    notes = db.Column(db.Text, default="")
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    property = db.relationship("Property", backref="electricity_bills", lazy=True)
    meter = db.relationship("ElectricityMeter", backref="bills", lazy=True)
    creator = db.relationship("User", foreign_keys=[created_by], lazy=True)


class ElectricityReading(BaseModel):
    __tablename__ = "electricity_readings"

    bill_id = db.Column(db.Integer, db.ForeignKey("electricity_bills.id"), nullable=False)
    meter_id = db.Column(db.Integer, db.ForeignKey("electricity_meters.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=True)
    prev_reading = db.Column(db.Numeric(10, 1), default=0)
    curr_reading = db.Column(db.Numeric(10, 1), default=0)
    usage = db.Column(db.Numeric(10, 1), default=0)
    calculated_amount = db.Column(db.Numeric(10, 2), default=0)
    confirmed_amount = db.Column(db.Numeric(10, 2), nullable=True)
    notes = db.Column(db.Text, default="")

    bill = db.relationship("ElectricityBill", backref="readings", lazy=True)
    meter = db.relationship("ElectricityMeter", backref="readings", lazy=True)
    room = db.relationship("Room", backref="electricity_readings", lazy=True)
