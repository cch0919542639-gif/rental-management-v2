"""
monthly_bill_paid_null_repair.py

Dry-run-first repair for imported monthly bills with paid=NULL.

Default behavior:
  - report monthly_bills where paid IS NULL
  - do not write changes

Execute mode:
  py -3 .\\scripts\\repair\\monthly_bill_paid_null_repair.py --execute
  py -3 .\\scripts\\repair\\monthly_bill_paid_null_repair.py --database-url sqlite:///D:\\CodexRuntime\\rental\\rebuild\\runtime-real.db --execute

Rollback:
  - Restore the database from backup if this normalization should be reverted.
  - This repair changes `monthly_bills.paid` from NULL -> 0 (False) only.
"""

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.db import db
from app.models import MonthlyBill
from scripts.repair._common import build_script_app


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first repair for monthly_bills.paid NULL values")
    parser.add_argument("--execute", action="store_true", help="Apply the repair instead of dry-run")
    parser.add_argument("--database-url", help="Override DATABASE_URL for this repair run")
    return parser


def main(argv: list[str]):
    args = _build_parser().parse_args(argv)
    execute = args.execute
    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url
    app = build_script_app()

    with app.app_context():
        candidates = MonthlyBill.query.filter(MonthlyBill.paid.is_(None)).order_by(MonthlyBill.id.asc()).all()
        print("=" * 72)
        print(f"MonthlyBill Paid NULL Repair ({'EXECUTE' if execute else 'DRY-RUN'})")
        print("=" * 72)
        print(f"Database URL: {os.getenv('DATABASE_URL', '(default runtime.db)')}")
        print(f"Candidate count: {len(candidates)}")
        print("Rollback note: restore from backup if NULL -> False normalization must be reverted.")
        for bill in candidates[:20]:
            print(
                f"  monthly_bill_id={bill.id} contract_id={bill.contract_id} "
                f"year_month={bill.year_month} paid={bill.paid}"
            )
        if len(candidates) > 20:
            print(f"  ... {len(candidates) - 20} more row(s)")

        if execute:
            for bill in candidates:
                bill.paid = False
            db.session.commit()
            print("-" * 72)
            print(f"Updated count: {len(candidates)}")
        else:
            print("-" * 72)
            print("Dry-run only. Re-run with --execute to apply changes.")
        print("=" * 72)


if __name__ == "__main__":
    main(sys.argv[1:])
