from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.core.db import db
from app.models import CalcMethod, Contract, Landlord, MonthlyBill, Property, Room, Tenant, User


@pytest.fixture()
def app():
    flask_app = create_app("testing")
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seeded_data(app):
    with app.app_context():
        user = User(username="admin", name="Admin", role="admin")
        user.set_password("admin123")
        db.session.add(user)

        landlord = Landlord(
            name="Owner A",
            phone="0912000000",
            electricity_rate_type="fixed",
            electricity_rate=Decimal("5"),
            water_rate_type="fixed",
            water_rate=Decimal("100"),
        )
        db.session.add(landlord)
        db.session.flush()

        prop = Property(
            landlord_id=landlord.id,
            name="North House",
            address="Taipei City",
            total_rooms=3,
            electricity_meter_type="independent",
            water_meter_type="shared",
            billing_rule="monthly",
        )
        db.session.add(prop)
        db.session.flush()

        room = Room(
            property_id=prop.id,
            room_number="A01",
            rent=Decimal("12000"),
            deposit=Decimal("24000"),
            status="occupied",
        )
        tenant = Tenant(name="Tenant One", phone="0912345678")
        calc_method = CalcMethod(name="Simple", module_key="simple_flat", description="Test calc")
        db.session.add_all([room, tenant, calc_method])
        db.session.flush()

        contract = Contract(
            tenant_id=tenant.id,
            room_id=room.id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            rent=Decimal("12000"),
            deposit=Decimal("24000"),
            electricity_rate=Decimal("5"),
            water_rate=Decimal("100"),
            status="active",
        )
        db.session.add(contract)
        db.session.flush()

        june_bill = MonthlyBill(
            contract_id=contract.id,
            year_month="202606",
            rent=Decimal("12000"),
            electricity_amount=Decimal("0"),
            public_electricity=Decimal("0"),
            water_amount=Decimal("0"),
            other_charges=Decimal("0"),
            total=Decimal("12000"),
            paid=False,
        )
        db.session.add(june_bill)
        db.session.commit()

        return {
            "user_id": user.id,
            "landlord_id": landlord.id,
            "property_id": prop.id,
            "room_id": room.id,
            "tenant_id": tenant.id,
            "contract_id": contract.id,
            "monthly_bill_id": june_bill.id,
            "calc_method_id": calc_method.id,
        }


@pytest.fixture()
def logged_in_client(client, seeded_data):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return client
