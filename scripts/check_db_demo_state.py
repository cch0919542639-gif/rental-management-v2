"""
check_db_demo_state.py

Phase 2 — Verify demo database consistency after seed_demo_data.py has run.

Checks:
  1. At least one User (admin) exists
  2. At least one Landlord exists
  3. At least one Property exists
  4. At least one Room exists
  5. At least one Tenant exists
  6. At least one Contract (active) exists
  7. MonthlyBills are present and linked to a Contract
  8. Relationships are valid (no orphan records)

Usage:
    cd D:\\CodexRuntime\\rental\\rebuild
    python scripts\\check_db_demo_state.py

Exit codes:
    0 — all checks passed
    1 — one or more consistency checks failed
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.core.db import db
from app.models import (
    Contract, Landlord, MonthlyBill, Property, Room, Tenant, User,
)


def main():
    app = create_app("default")
    errors = []

    with app.app_context():
        # 1. User
        user_count = User.query.count()
        if user_count == 0:
            errors.append("CRITICAL: No users found — seed has not been run?")
        else:
            admin = User.query.filter_by(username="admin").first()
            if admin is None:
                errors.append("WARNING: 'admin' user not found.")

        # 2. Landlord
        landlord_count = Landlord.query.count()
        if landlord_count == 0:
            errors.append("CRITICAL: No landlords found.")

        # 3. Property
        prop_count = Property.query.count()
        if prop_count == 0:
            errors.append("CRITICAL: No properties found.")
        else:
            orphans = Property.query.filter(
                ~Property.landlord_id.in_(
                    db.session.query(Landlord.id)
                )
            ).count()
            if orphans > 0:
                errors.append(f"WARNING: {orphans} property(ies) reference a non-existent landlord.")

        # 4. Room
        room_count = Room.query.count()
        if room_count == 0:
            errors.append("CRITICAL: No rooms found.")
        else:
            orphan_rooms = Room.query.filter(
                ~Room.property_id.in_(db.session.query(Property.id))
            ).count()
            if orphan_rooms > 0:
                errors.append(f"WARNING: {orphan_rooms} room(s) reference a non-existent property.")

        # 5. Tenant
        tenant_count = Tenant.query.count()
        if tenant_count == 0:
            errors.append("CRITICAL: No tenants found.")

        # 6. Contract
        contract_count = Contract.query.count()
        if contract_count == 0:
            errors.append("CRITICAL: No contracts found.")
        else:
            active = Contract.query.filter_by(status="active").count()
            if active == 0:
                errors.append("WARNING: No active contracts found.")
            orphan_contracts = Contract.query.filter(
                ~Contract.room_id.in_(db.session.query(Room.id))
            ).count()
            if orphan_contracts > 0:
                errors.append(f"WARNING: {orphan_contracts} contract(s) reference a non-existent room.")

        # 7. MonthlyBills
        bill_count = MonthlyBill.query.count()
        if bill_count == 0:
            errors.append("CRITICAL: No monthly bills found.")
        else:
            orphan_bills = MonthlyBill.query.filter(
                ~MonthlyBill.contract_id.in_(db.session.query(Contract.id))
            ).count()
            if orphan_bills > 0:
                errors.append(f"WARNING: {orphan_bills} monthly bill(s) reference a non-existent contract.")

        # 8. Summary
        print("=" * 54)
        print("  Demo DB State Check Report")
        print("=" * 54)
        print(f"  Users:          {user_count}")
        print(f"  Landlords:      {landlord_count}")
        print(f"  Properties:     {prop_count}")
        print(f"  Rooms:          {room_count}")
        print(f"  Tenants:        {tenant_count}")
        print(f"  Contracts:      {contract_count}  (active: {Contract.query.filter_by(status='active').count()})")
        print(f"  Monthly Bills:  {bill_count}")
        print("=" * 54)

        if errors:
            print("  ISSUES FOUND:")
            for err in errors:
                print(f"    - {err}")
            print("=" * 54)
            return 1
        else:
            print("  All checks passed — demo data is consistent.")
            print("=" * 54)
            return 0


if __name__ == "__main__":
    sys.exit(main())
