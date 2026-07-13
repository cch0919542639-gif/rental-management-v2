r"""Set one monthly bill's verified carry-forward balance with dry-run protection.

Usage:
    py -3 .\scripts\repair\monthly_bill_previous_balance_repair.py `
      --database-url sqlite:///D:\CodexRuntime\rental\rebuild\runtime-real.db `
      --bill-id 819 --amount 25047

Rollback: restore the database backup made before --execute, or rerun with the
reviewed prior amount after confirming the affected bill.
"""

from __future__ import annotations

import argparse
import os
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first monthly bill previous-balance repair")
    parser.add_argument("--database-url", required=True, help="Explicit target database URL")
    parser.add_argument("--bill-id", type=int, required=True, help="Monthly bill ID to repair")
    parser.add_argument("--amount", type=Decimal, required=True, help="Verified carry-forward amount")
    parser.add_argument("--execute", action="store_true", help="Persist the requested previous balance")
    return parser


def _money(amount: Decimal) -> str:
    return f"{amount.quantize(Decimal('1')):,.0f}"


def main(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    if args.amount < 0:
        raise SystemExit("Previous balance cannot be negative.")
    os.environ["DATABASE_URL"] = args.database_url
    os.environ.setdefault("SCRIPT_APP_CONFIG", "default")

    from app.core.db import db
    from app.models import MonthlyBill
    from app.repositories import BillingRepository
    from app.services import BillingService
    from scripts.repair._common import build_script_app

    app = build_script_app()
    with app.app_context():
        bill = BillingRepository.get_or_404(args.bill_id)
        old_balance = Decimal(str(bill.previous_balance or 0))
        old_total = Decimal(str(bill.total or 0))
        bill.previous_balance = args.amount
        new_total = BillingService.calculate_total(bill)
        bill.previous_balance = old_balance
        bill.total = old_total

        print("=" * 72)
        print(f"MonthlyBill Previous Balance Repair ({'EXECUTE' if args.execute else 'DRY-RUN'})")
        print("=" * 72)
        print(f"Database URL: {args.database_url}")
        print(f"Bill ID: {bill.id}, contract_id={bill.contract_id}, year_month={bill.year_month}")
        print(f"Previous balance: {_money(old_balance)} -> {_money(args.amount)}")
        print(f"Total: {_money(old_total)} -> {_money(new_total)}")
        print("Rollback note: restore the pre-execute backup or reapply the reviewed prior amount.")

        if args.execute:
            bill.previous_balance = args.amount
            BillingService.calculate_total(bill)
            db.session.commit()
            print("Updated count: 1")
        else:
            print("Dry-run only. Re-run with --execute to apply changes.")
        print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
