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

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.repair._common import build_script_app, parse_reference_date
from app.models import Contract
from app.services import ContractService


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first contract expiry repair")
    parser.add_argument("--execute", action="store_true", help="Apply the repair instead of dry-run")
    parser.add_argument(
        "--reference-date",
        help="ISO date used to detect expired active contracts. Default: today.",
    )
    return parser


def main(argv: list[str]):
    args = _build_parser().parse_args(argv)
    execute = args.execute
    reference_date = parse_reference_date(args.reference_date)
    app = build_script_app()

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
        print("Rollback note: this repair only changes Contract.status from active -> expired.")
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
