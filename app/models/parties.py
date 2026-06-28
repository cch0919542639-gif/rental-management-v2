from app.core.db import db
from app.models.base import BaseModel


class Landlord(BaseModel):
    __tablename__ = "landlords"

    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    electricity_account = db.Column(db.String(50))
    water_account = db.Column(db.String(50))
    electricity_rate_type = db.Column(db.String(20), default="fixed")
    electricity_rate = db.Column(db.Numeric(8, 2), default=0)
    water_rate_type = db.Column(db.String(20), default="fixed")
    water_rate = db.Column(db.Numeric(8, 2), default=0)
    notes = db.Column(db.Text)

    properties = db.relationship("Property", backref="landlord", lazy=True)
    user = db.relationship("User", backref="landlord", lazy=True, uselist=False)


class Property(BaseModel):
    __tablename__ = "properties"

    landlord_id = db.Column(db.Integer, db.ForeignKey("landlords.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    total_rooms = db.Column(db.Integer, default=0)
    electricity_meter_type = db.Column(db.String(20), default="independent")
    water_meter_type = db.Column(db.String(20), default="independent")
    billing_rule = db.Column(db.String(50), default="proportion")

    rooms = db.relationship("Room", backref="property", lazy=True, cascade="all, delete-orphan")


class Room(BaseModel):
    __tablename__ = "rooms"

    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    room_number = db.Column(db.String(20), nullable=False)
    rent = db.Column(db.Numeric(10, 2), default=0)
    deposit = db.Column(db.Numeric(10, 2), default=0)
    electricity_meter_id = db.Column(db.String(50))
    water_meter_id = db.Column(db.String(50))
    area_ping = db.Column(db.Numeric(8, 1))
    status = db.Column(db.String(20), default="vacant")
    notes = db.Column(db.Text)

    contracts = db.relationship("Contract", backref="room", lazy=True)

    __table_args__ = (db.UniqueConstraint("property_id", "room_number", name="uq_room_property_room_number"),)


class Tenant(BaseModel):
    __tablename__ = "tenants"

    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    id_number = db.Column(db.String(20))
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)

    contracts = db.relationship("Contract", backref="tenant", lazy=True)


class Contract(BaseModel):
    __tablename__ = "contracts"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    rent = db.Column(db.Numeric(10, 2), nullable=False)
    deposit = db.Column(db.Numeric(10, 2), default=0)
    electricity_rate = db.Column(db.Numeric(8, 2))
    water_rate = db.Column(db.Numeric(8, 2))
    status = db.Column(db.String(20), default="active")
    notes = db.Column(db.Text)
    start_electricity_reading = db.Column(db.Numeric(10, 1))
    start_water_reading = db.Column(db.Numeric(10, 1))

    bills = db.relationship("MonthlyBill", backref="contract", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship("PaymentRecord", backref="contract", lazy=True)
