"""
Read-only-first SQLite export scaffold for Phase 5 drill.

Purpose:
  - Inspect the current SQLite database in FK-safe table order
  - Preview row counts before PostgreSQL migration
  - Optionally export CSV files plus a manifest for manual import drills

Rollback:
  - Delete the generated output directory if an export run should be discarded.
  - No database writes occur; this script never mutates the source database.

Verification:
  - Run without `--execute` first and review the table order and row counts.
  - After `--execute`, verify `manifest.json` exists and CSV counts match the manifest.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
import sys

from sqlalchemy import create_engine, select

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.core.db import db
from scripts.db_runtime_common import get_database_url, get_db_dialect


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first SQLite export scaffold for PostgreSQL drills.")
    parser.add_argument("--source-url", help="Override source database URL. Defaults to DATABASE_URL.")
    parser.add_argument("--output-dir", default="migration_exports", help="Directory for CSV/manifest output.")
    parser.add_argument("--execute", action="store_true", help="Actually write CSV files and manifest.")
    return parser


def _serialize_value(value):
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _build_table_plan(source_url: str):
    app = create_app("default")
    engine = create_engine(source_url)
    plans = []
    with app.app_context(), engine.connect() as conn:
        for table in db.metadata.sorted_tables:
            rows = conn.execute(select(table)).mappings().all()
            plans.append(
                {
                    "table_name": table.name,
                    "columns": [column.name for column in table.columns],
                    "row_count": len(rows),
                    "rows": rows,
                }
            )
    return plans


def _write_export(output_dir: Path, source_url: str, plans):
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source_url": source_url,
        "source_dialect": get_db_dialect(source_url),
        "table_order": [plan["table_name"] for plan in plans],
        "tables": [
            {
                "table_name": plan["table_name"],
                "row_count": plan["row_count"],
                "file": f"{plan['table_name']}.csv",
            }
            for plan in plans
        ],
    }
    for plan in plans:
        csv_path = output_dir / f"{plan['table_name']}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=plan["columns"])
            writer.writeheader()
            for row in plan["rows"]:
                writer.writerow({key: _serialize_value(value) for key, value in row.items()})

    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    args = _build_parser().parse_args()
    source_url = args.source_url or get_database_url()
    source_dialect = get_db_dialect(source_url)
    if source_dialect != "sqlite":
        raise SystemExit(f"export_sqlite_to_pg.py requires a sqlite source URL. Got: {source_dialect or 'unknown'}")

    plans = _build_table_plan(source_url)
    total_rows = sum(plan["row_count"] for plan in plans)
    output_dir = Path(args.output_dir)

    print("=" * 72)
    print("SQLite Export Drill")
    print("=" * 72)
    print(f"Mode       : {'EXECUTE' if args.execute else 'DRY-RUN'}")
    print(f"Source     : {source_url}")
    print(f"Output Dir : {output_dir.resolve()}")
    print("-" * 72)
    for plan in plans:
        print(f"{plan['table_name']}: {plan['row_count']} row(s)")
    print("-" * 72)
    print(f"Tables     : {len(plans)}")
    print(f"Total Rows : {total_rows}")

    if not args.execute:
        print("Dry-run only. Re-run with --execute to write CSV files and manifest.")
        print("=" * 72)
        return

    _write_export(output_dir, source_url, plans)
    print("Export complete. Generated CSV files and manifest.json.")
    print("=" * 72)


if __name__ == "__main__":
    main()
