"""
contract_expiry_repair.py

Dry-run-first repair for expired contracts.

Default behavior:
  - report contracts where status='active' and end_date < reference_date
  - do not write changes

Execute mode:
  py -3 .\\scripts\\repair\\contract_expiry_repair.py --execute

Usage:
    cd D:\\CodexRuntime\\rental\\rebuild
    py -3 .\\scripts\\repair\\contract_expiry_repair.py
"""

from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.models import Contract
from app.services import ContractService


def main(argv: list[str]):
    execute = "--execute" in argv
    reference_date = date.today()
    app = create_app("default")

    with app.app_context():
        candidates = (
            Contract.query.filter(Contract.status == "active", Contract.end_date < reference_date)
            .order_by(Contract.end_date.asc(), Contract.id.asc())
            .all()
        )
        print("=" * 72)
        print(f"Contract Expiry Repair ({'EXECUTE' if execute else 'DRY-RUN'})")
        print("=" * 72)
        print(f"Reference date: {reference_date.isoformat()}")
        print(f"Candidate count: {len(candidates)}")
        for contract in candidates:
            print(
                f"  contract_id={contract.id} room_id={contract.room_id} "
                f"tenant_id={contract.tenant_id} end_date={contract.end_date} status={contract.status}"
            )

        if execute:
            updated = ContractService.sync_expired_contracts(reference_date=reference_date)
            print("-" * 72)
            print(f"Updated count: {len(updated)}")
        else:
            print("-" * 72)
            print("Dry-run only. Re-run with --execute to apply changes.")
        print("=" * 72)


if __name__ == "__main__":
    main(sys.argv[1:])
