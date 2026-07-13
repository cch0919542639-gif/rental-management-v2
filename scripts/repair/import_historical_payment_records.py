r"""Import reviewed Google Sheet payment rows through the PaymentRecord state machine.

The input CSV must contain:
monthly_bill_id,amount,payer_name,source_month,source_row,transaction_date,bank_name,account_number

`transaction_date` may be empty when the Sheet has no date evidence. A stable
transaction ID is derived from the Sheet month, row, and bill ID, making a
reviewed import safe to rerun without creating duplicates.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED_COLUMNS = {
    "monthly_bill_id",
    "amount",
    "payer_name",
    "source_month",
    "source_row",
    "transaction_date",
    "bank_name",
    "account_number",
}


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first historical payment record import")
    parser.add_argument("--database-url", required=True, help="Explicit target database URL")
    parser.add_argument("--csv", type=Path, required=True, help="Reviewed payment candidate CSV")
    parser.add_argument("--execute", action="store_true", help="Persist verified and linked payment records")
    return parser


def _money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('1')):,.0f}"


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise SystemExit(f"CSV missing required columns: {', '.join(sorted(missing))}")
        return list(reader)


def _transaction_id(row: dict[str, str]) -> str:
    return f"legacy-sheet-{row['source_month']}-row{row['source_row']}-bill{row['monthly_bill_id']}"


def main(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    rows = _load_rows(args.csv)
    os.environ["DATABASE_URL"] = args.database_url
    os.environ.setdefault("SCRIPT_APP_CONFIG", "default")

    from app.repositories import BillingRepository, PaymentRepository
    from app.services import PaymentService
    from scripts.repair._common import build_script_app

    app = build_script_app()
    created = skipped = 0
    with app.app_context():
        print(f"Historical Payment Import ({'EXECUTE' if args.execute else 'DRY-RUN'})")
        print(f"Database URL: {args.database_url}")
        for row in rows:
            bill_id = int(row["monthly_bill_id"])
            amount = Decimal(row["amount"])
            if amount <= 0:
                raise SystemExit(f"bill {bill_id}: amount must be positive")
            bill = BillingRepository.get_or_404(bill_id)
            transaction_id = _transaction_id(row)
            existing = PaymentRepository.get_by_transaction_id(transaction_id)
            if existing:
                skipped += 1
                print(f"SKIP existing bill={bill.id} transaction_id={transaction_id}")
                continue

            transaction_date = row["transaction_date"].strip() or None
            if transaction_date:
                transaction_date = date.fromisoformat(transaction_date)
            print(
                f"CANDIDATE bill={bill.id} contract={bill.contract_id} amount={_money(amount)} "
                f"sheet={row['source_month']} row={row['source_row']}"
            )
            if not args.execute:
                continue

            record = PaymentService.create_payment_record(
                monthly_bill_id=bill.id,
                contract_id=bill.contract_id,
                amount=amount,
                transaction_date=transaction_date,
                payer_name=row["payer_name"].strip() or None,
                bank_name=row["bank_name"].strip() or None,
                account_number=row["account_number"].strip() or None,
                transaction_id=transaction_id,
                status_text="historical_sheet",
                notes=f"歷史付款匯入：Google Sheet {row['source_month']} 第 {row['source_row']} 列",
            )
            PaymentService.verify_payment(record, notes=record.notes)
            PaymentService.link_payment(record, monthly_bill_id=bill.id, notes=record.notes)
            created += 1

    print(f"Created: {created}; skipped existing: {skipped}; candidates: {len(rows)}")
    if not args.execute:
        print("Dry-run only. Re-run with --execute to create verified, linked PaymentRecord rows.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
