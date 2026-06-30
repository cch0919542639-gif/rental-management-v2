"""
maintenance_legacy_scan.py

Read-only legacy maintenance scan for Phase 2B migration preparation.

Scope:
  C1. Identify virtual tenant names that should become MaintenanceRequest
  C2. Identify room-linked candidates that need maintenance request creation
  C3. Identify room statuses outside the frozen allowed set

This script does NOT write to the database.

Usage:
    cd D:\\CodexRuntime\\rental\\rebuild
    py -3 .\\scripts\\migration\\maintenance_legacy_scan.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.migration._common import build_script_app
from app.models import Contract, Room, Tenant

FORBIDDEN_TENANT_NAMES = {"空房", "待修", "待補", "倉庫", "鐵皮"}
ALLOWED_ROOM_STATUSES = {"vacant", "occupied"}


def main():
    app = build_script_app()

    with app.app_context():
        virtual_tenants = Tenant.query.filter(Tenant.name.in_(FORBIDDEN_TENANT_NAMES)).order_by(Tenant.id.asc()).all()
        invalid_rooms = Room.query.filter(~Room.status.in_(ALLOWED_ROOM_STATUSES)).order_by(Room.id.asc()).all()

        candidate_rows = []
        for tenant in virtual_tenants:
            contracts = Contract.query.filter_by(tenant_id=tenant.id).all()
            for contract in contracts:
                room = contract.room
                candidate_rows.append(
                    {
                        "tenant_id": tenant.id,
                        "tenant_name": tenant.name,
                        "contract_id": contract.id,
                        "room_id": room.id if room else None,
                        "property_name": room.property.name if room and room.property else None,
                        "room_number": room.room_number if room else None,
                        "contract_status": contract.status,
                    }
                )

        print("=" * 64)
        print("Maintenance Legacy Scan (read-only)")
        print("=" * 64)
        print(f"Virtual tenant rows: {len(virtual_tenants)}")
        print(f"Maintenance request candidates (C2): {len(candidate_rows)}")
        print(f"Invalid room statuses (C3): {len(invalid_rooms)}")
        print("=" * 64)

        if virtual_tenants:
            print("C1/C2 candidates:")
            for item in candidate_rows:
                print(
                    f"  tenant={item['tenant_name']}#{item['tenant_id']} "
                    f"contract={item['contract_id']} room={item['property_name']} / {item['room_number']} "
                    f"status={item['contract_status']}"
                )
            print("=" * 64)

        if invalid_rooms:
            print("C3 invalid room statuses:")
            for room in invalid_rooms:
                print(
                    f"  room_id={room.id} property={room.property.name if room.property else '-'} "
                    f"room={room.room_number} status={room.status}"
                )
            print("=" * 64)

        if not virtual_tenants and not invalid_rooms:
            print("No legacy maintenance migration candidates found.")
            print("=" * 64)


if __name__ == "__main__":
    main()
