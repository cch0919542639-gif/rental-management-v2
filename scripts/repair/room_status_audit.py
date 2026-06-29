"""
room_status_audit.py

Read-only audit for room status normalization.

Allowed values:
  - vacant
  - occupied

Usage:
    cd D:\\CodexRuntime\\rental\\rebuild
    py -3 .\\scripts\\repair\\room_status_audit.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.repair._common import build_script_app
from app.models import Room

ALLOWED = {"vacant", "occupied"}


def main():
    app = build_script_app()
    with app.app_context():
        values = sorted({item.status for item in Room.query.all() if item.status is not None})
        invalid_rooms = [item for item in Room.query.all() if item.status not in ALLOWED]

        print("=" * 72)
        print("Room Status Audit (read-only)")
        print("=" * 72)
        print(f"Distinct values: {values}")
        print(f"Invalid rows: {len(invalid_rooms)}")
        for room in invalid_rooms:
            print(
                f"  room_id={room.id} property={room.property.name if room.property else '-'} "
                f"room={room.room_number} status={room.status}"
            )
        print("=" * 72)


if __name__ == "__main__":
    main()
