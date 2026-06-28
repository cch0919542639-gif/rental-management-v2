from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.core.db import db
from app.models import CalcMethod, Contract, Landlord, MonthlyBill, Property, Room, Tenant, User


def main():
    app = create_app("default")

    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(username="admin", name="Admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        landlord = Landlord(
            name="Owner Demo",
            phone="0912000000",
            electricity_account="E-001",
            water_account="W-001",
            electricity_rate_type="fixed",
            electricity_rate=Decimal("5"),
            water_rate_type="fixed",
            water_rate=Decimal("100"),
            notes="Demo landlord",
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
            area_ping=Decimal("8.5"),
            status="occupied",
            notes="Demo room",
        )
        tenant = Tenant(
            name="Tenant Demo",
            phone="0912345678",
            emergency_contact="Parent Demo",
            emergency_phone="0922333444",
        )
        calc_method = CalcMethod(name="Simple", module_key="simple_flat", description="Demo calc method")
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
            notes="Demo contract",
        )
        db.session.add(contract)
        db.session.flush()

        monthly_bills = [
            MonthlyBill(
                contract_id=contract.id,
                year_month="202606",
                rent=Decimal("12000"),
                electricity_amount=Decimal("500"),
                electricity_usage=Decimal("50"),
                water_amount=Decimal("300"),
                water_usage=Decimal("10"),
                other_charges=Decimal("80"),
                total=Decimal("12880"),
                paid=True,
            ),
            MonthlyBill(
                contract_id=contract.id,
                year_month="202607",
                rent=Decimal("12000"),
                electricity_amount=Decimal("620"),
                electricity_usage=Decimal("62"),
                water_amount=Decimal("320"),
                water_usage=Decimal("11"),
                other_charges=Decimal("0"),
                total=Decimal("12940"),
                paid=False,
            ),
        ]
        db.session.add_all(monthly_bills)
        db.session.commit()

        print("Seed complete")
        print("Login: admin / admin123")
        print("Property: North House")
        print("Tenant: Tenant Demo")


if __name__ == "__main__":
    main()
