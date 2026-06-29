"""
year_month_audit.py

Read-only audit for `year_month` normalization.

Checks:
  - monthly_bills.year_month distinct lengths
  - electricity_bills.year_month distinct lengths
  - non-6-char values

Usage:
    cd D:\\CodexRuntime\\rental\\rebuild
    py -3 .\\scripts\\repair\\year_month_audit.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import func

from app import create_app
from app.core.db import db
from app.models import ElectricityBill, MonthlyBill


def _print_lengths(label, model):
    rows = (
        db.session.query(func.length(model.year_month).label("length"), func.count(model.id).label("count"))
        .group_by(func.length(model.year_month))
        .order_by(func.length(model.year_month).asc())
        .all()
    )
    print(f"[{label}] distinct lengths")
    for row in rows:
        print(f"  length={row.length} count={row.count}")


def _print_anomalies(label, model):
    rows = (
        model.query.filter(model.year_month.isnot(None), func.length(model.year_month) != 6)
        .order_by(model.id.asc())
        .all()
    )
    print(f"[{label}] anomalies={len(rows)}")
    for row in rows:
        print(f"  id={row.id} year_month={row.year_month}")


def main():
    app = create_app("default")
    with app.app_context():
        print("=" * 72)
        print("Year Month Audit (read-only)")
        print("=" * 72)
        _print_lengths("monthly_bills", MonthlyBill)
        _print_anomalies("monthly_bills", MonthlyBill)
        print("-" * 72)
        _print_lengths("electricity_bills", ElectricityBill)
        _print_anomalies("electricity_bills", ElectricityBill)
        print("=" * 72)


if __name__ == "__main__":
    main()
