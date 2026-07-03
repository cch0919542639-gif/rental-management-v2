"""
import_csv_to_target.py — Import CSV data into runtime-real.db.

Default: dry-run (no writes). Use --execute to commit.

Flow:
  1. Read manifest to determine table order (respecting FK dependencies)
  2. For each table, read its CSV, INSERT or REPLACE rows
  3. Print row counts and execution summary

Usage:
    py -3 scripts/import_csv_to_target.py                    # dry-run
    py -3 scripts/import_csv_to_target.py --execute          # actual import
    py -3 scripts/import_csv_to_target.py --table monthly_bills  # single table dry-run
"""

import argparse, csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

MANIFEST = PROJECT / "real_import" / "manifest.json"
IMPORT_DIR = PROJECT / "real_import"
TARGET_DB = "sqlite:///" + str(PROJECT / "runtime-real.db")


def _normalize_row(table: str, row: dict[str, str]):
    clean = {k: (v if v != "" else None) for k, v in row.items()}

    if table == "monthly_bills":
        if clean.get("paid") is None:
            clean["paid"] = 0

    return clean


def _build_parser():
    p = argparse.ArgumentParser(description="Import CSV data into runtime-real.db")
    p.add_argument("--execute", action="store_true", help="Actually commit the import")
    p.add_argument("--table", help="Import only one table by name (dry-run or execute)")
    return p


def main():
    from sqlalchemy import create_engine, inspect, text

    args = _build_parser().parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    engine = create_engine(TARGET_DB)
    inspector = inspect(engine)
    mode = "EXECUTE" if args.execute else "DRY-RUN"

    print("=" * 72)
    print(f" CSV Import to runtime-real.db — {mode}")
    print("=" * 72)

    tables = manifest["tables"]
    if args.table:
        tables = [e for e in tables if e["table"] == args.table]
        if not tables:
            raise SystemExit(f"Unknown table: {args.table}")

    total_rows = 0
    with engine.begin() as conn:
        for entry in tables:
            table = entry["table"]
            pk = entry["primary_key"]
            csv_path = IMPORT_DIR / f"{table}.csv"

            if not csv_path.exists():
                print(f"  SKIP {table}: CSV not found")
                continue

            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                print(f"  EMPTY {table}")
                continue

            columns = list(rows[0].keys())
            placeholders = ", ".join([f":{c}" for c in columns])
            col_list = ", ".join(columns)

            # Infer INSERT OR REPLACE for idempotency
            upsert = f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})"

            if not args.execute:
                print(f"  [DRY-RUN] {table}: {len(rows)} rows would be inserted")
            else:
                for row in rows:
                    clean = _normalize_row(table, row)
                    conn.execute(text(upsert), clean)
                print(f"  [INSERT] {table}: {len(rows)} rows")

            total_rows += len(rows)

    print("=" * 72)
    print(f" Total rows processed: {total_rows}")
    if not args.execute:
        print(" Dry-run only. Run with --execute to commit.")
    else:
        print(" Import committed.")
    print("=" * 72)


if __name__ == "__main__":
    main()
