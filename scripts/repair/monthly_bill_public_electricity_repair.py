r"""Correct a verified monthly-bill public-electricity component safely.

Usage:
    py -3 .\scripts\repair\monthly_bill_public_electricity_repair.py `
      --database-url sqlite:///D:\CodexRuntime\rental\rebuild\runtime-real.db `
      --bill-id 943 --amount 0

The script defaults to dry-run and always recomputes the total from the
official bill formula before it writes.
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
    parser = argparse.ArgumentParser(description="Dry-run-first monthly bill public-electricity repair")
    parser.add_argument("--database-url", required=True, help="Explicit target database URL")
    parser.add_argument("--bill-id", type=int, required=True, help="Monthly bill ID to repair")
    parser.add_argument("--amount", type=Decimal, required=True, help="Verified public electricity amount")
    parser.add_argument("--execute", action="store_true", help="Persist the requested public electricity amount")
    return parser


def _money(amount: Decimal) -> str:
    return f"{amount.quantize(Decimal('1')):,.0f}"


def main(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    if args.amount < 0:
        raise SystemExit("Public electricity cannot be negative.")
    os.environ["DATABASE_URL"] = args.database_url
    os.environ.setdefault("SCRIPT_APP_CONFIG", "default")

    from app.core.db import db
    from app.repositories import BillingRepository
    from app.services import BillingService
    from scripts.repair._common import build_script_app

    app = build_script_app()
    with app.app_context():
        bill = BillingRepository.get_or_404(args.bill_id)
        old_amount = Decimal(str(bill.public_electricity or 0))
        old_total = Decimal(str(bill.total or 0))
        bill.public_electricity = args.amount
        new_total = BillingService.calculate_total(bill)
        bill.public_electricity = old_amount
        bill.total = old_total

        print("=" * 72)
        print(f"MonthlyBill Public Electricity Repair ({'EXECUTE' if args.execute else 'DRY-RUN'})")
        print("=" * 72)
        print(f"Database URL: {args.database_url}")
        print(f"Bill ID: {bill.id}, contract_id={bill.contract_id}, year_month={bill.year_month}")
        print(f"Public electricity: {_money(old_amount)} -> {_money(args.amount)}")
        print(f"Total: {_money(old_total)} -> {_money(new_total)}")
        print("Rollback note: restore the database backup or reapply the reviewed component amount.")

        if args.execute:
            bill.public_electricity = args.amount
            BillingService.calculate_total(bill)
            db.session.commit()
            print("Updated count: 1")
        else:
            print("Dry-run only. Re-run with --execute to apply changes.")
        print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
