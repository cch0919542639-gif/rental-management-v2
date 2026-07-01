"""
Dry-run-first target schema preparation scaffold for Phase 5 bridge drills.

Purpose:
  - Inspect a target database before rehearsal import
  - Report existing managed tables and row counts
  - Optionally create missing application tables on an empty rehearsal target

Rollback:
  - Drop and recreate the rehearsal target database from scratch, or restore from backup.
  - This script does not modify the source database.

Verification:
  - Run without --execute first and confirm the target is empty / safe.
  - After --execute, confirm the expected managed tables exist and row counts remain zero.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from sqlalchemy import create_engine, func, inspect, select

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.core.db import db
from scripts.db_runtime_common import get_db_dialect


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first target schema preparation for bridge drills.")
    parser.add_argument("--target-url", required=True, help="Target database URL")
    parser.add_argument("--execute", action="store_true", help="Actually create missing tables")
    parser.add_argument(
        "--allow-nonempty",
        action="store_true",
        help="Allow execution when existing managed tables already contain rows",
    )
    return parser


def main():
    args = _build_parser().parse_args()
    app = create_app("default")
    engine = create_engine(args.target_url)
    managed_tables = [table.name for table in db.metadata.sorted_tables]

    print("=" * 72)
    print("Target DB Preparation")
    print("=" * 72)
    print(f"Mode       : {'EXECUTE' if args.execute else 'DRY-RUN'}")
    print(f"Target URL : {args.target_url}")
    print(f"Dialect    : {get_db_dialect(args.target_url) or 'unknown'}")
    print("-" * 72)

    with app.app_context(), engine.begin() as conn:
        inspector = inspect(conn)
        existing_tables = set(inspector.get_table_names())
        missing_tables = [name for name in managed_tables if name not in existing_tables]
        nonempty_tables = []

        for table in db.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            row_count = conn.execute(select(func.count()).select_from(table)).scalar_one()
            print(f"{table.name}: existing_rows={row_count}")
            if row_count:
                nonempty_tables.append((table.name, row_count))

        print("-" * 72)
        print(f"Managed tables : {len(managed_tables)}")
        print(f"Missing tables : {len(missing_tables)}")
        if missing_tables:
            print("Would create   : " + ", ".join(missing_tables))
        else:
            print("Would create   : none")

        if nonempty_tables and not args.allow_nonempty:
            detail = ", ".join(f"{name}={count}" for name, count in nonempty_tables)
            raise SystemExit(
                "Target contains existing rehearsal data; refusing to proceed without --allow-nonempty. "
                f"Non-empty tables: {detail}"
            )

        if not args.execute:
            print("Dry-run only. Re-run with --execute to create missing tables.")
            print("=" * 72)
            return

        db.metadata.create_all(bind=conn)
        print("Target schema prepared.")
        print("=" * 72)


if __name__ == "__main__":
    main()
