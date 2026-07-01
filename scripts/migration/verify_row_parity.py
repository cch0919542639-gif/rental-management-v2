"""
Read-only row-count parity checker for Phase 5 migration drills.

Purpose:
  - Compare per-table row counts between source and target databases
  - Detect missing tables or mismatched counts before cutover

Rollback:
  - No rollback needed; this script is read-only.

Verification:
  - Run against known-identical databases first and confirm PASS.
  - Run after export/import drills and confirm zero mismatches.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from sqlalchemy import create_engine, func, select

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.core.db import db
from scripts.db_runtime_common import get_database_url, get_db_dialect


def _build_parser():
    parser = argparse.ArgumentParser(description="Compare per-table row counts between source and target databases.")
    parser.add_argument("--source-url", required=True, help="Source database URL")
    parser.add_argument("--target-url", required=True, help="Target database URL")
    parser.add_argument("--table", action="append", dest="tables", help="Optional table filter; may be repeated")
    return parser


def _collect_counts(database_url: str, selected_tables: set[str] | None):
    app = create_app("default")
    engine = create_engine(database_url)
    counts = {}
    with app.app_context(), engine.connect() as conn:
        for table in db.metadata.sorted_tables:
            if selected_tables and table.name not in selected_tables:
                continue
            counts[table.name] = conn.execute(select(func.count()).select_from(table)).scalar_one()
    return counts


def main():
    args = _build_parser().parse_args()
    selected_tables = set(args.tables or [])
    source_counts = _collect_counts(args.source_url, selected_tables or None)
    target_counts = _collect_counts(args.target_url, selected_tables or None)
    all_tables = [table.name for table in db.metadata.sorted_tables if not selected_tables or table.name in selected_tables]

    mismatches = []
    print("=" * 72)
    print("Row Parity Check")
    print("=" * 72)
    print(f"Source : {get_db_dialect(args.source_url)}")
    print(f"Target : {get_db_dialect(args.target_url)}")
    print("-" * 72)
    for table_name in all_tables:
        source_count = source_counts.get(table_name)
        target_count = target_counts.get(table_name)
        status = "OK" if source_count == target_count else "MISMATCH"
        print(f"{table_name}: source={source_count} target={target_count} [{status}]")
        if status != "OK":
            mismatches.append(table_name)
    print("-" * 72)
    if mismatches:
        print(f"Result : FAIL ({len(mismatches)} mismatched table(s))")
        print("=" * 72)
        raise SystemExit(1)

    print("Result : PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
