"""Incrementally import a Batch 2 whitelist bundle into an existing target DB.

The importer is dry-run-first and does not use upsert semantics.  Any existing
primary key is a stop condition, which prevents accidental overwrites of Batch
1 data.  Run the guarded policy assignment only after this importer succeeds.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "real_import" / "batch2"
DEFAULT_DATABASE_URL = f"sqlite:///{PROJECT_ROOT / 'runtime-real.db'}"
REQUIRED_PROPERTIES = (1, 2, 3, 4, 5, 6, 21, 22)


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first incremental Batch 2 whitelist importer")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR, help="Export bundle directory")
    parser.add_argument("--database-url", default=DEFAULT_DATABASE_URL, help="Target database URL")
    parser.add_argument("--execute", action="store_true", help="Commit the approved CSV bundle")
    return parser


def _load_bundle(input_dir):
    manifest_path = input_dir / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Batch 2 manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("batch") != "batch2" or tuple(manifest.get("approved_property_ids", ())) != REQUIRED_PROPERTIES:
        raise RuntimeError("Manifest is not the approved Batch 2 whitelist bundle.")
    bundle = []
    for entry in sorted(manifest["tables"], key=lambda item: item["order"]):
        path = input_dir / f"{entry['table']}.csv"
        if not path.is_file():
            raise RuntimeError(f"CSV missing for {entry['table']}: {path}")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = [{key: (value if value != "" else None) for key, value in row.items()} for row in csv.DictReader(handle)]
        if entry["table"] == "monthly_bills":
            for row in rows:
                row["previous_balance"] = row.get("previous_balance") or 0
        if len(rows) != entry["rows"]:
            raise RuntimeError(f"CSV row count mismatch for {entry['table']}")
        bundle.append((entry, rows))
    return bundle


def _validate_target(engine, bundle):
    inspector = inspect(engine)
    for entry, rows in bundle:
        table = entry["table"]
        if not inspector.has_table(table):
            raise RuntimeError(f"Target database is missing table: {table}")
        existing_columns = {column["name"] for column in inspector.get_columns(table)}
        if rows:
            missing = set(rows[0]) - existing_columns
            if missing:
                hint = ""
                if table in {"properties", "rooms"} and {
                    "electricity_policy_code",
                    "water_policy_code",
                } & missing:
                    hint = (
                        " Apply migration 20260703_000003_utility_policy_codes to the target "
                        "after taking a backup, then retry this dry-run."
                    )
                raise RuntimeError(f"Target table {table} is missing columns: {', '.join(sorted(missing))}.{hint}")


def _assert_no_primary_key_collisions(conn, bundle):
    collisions = []
    for entry, rows in bundle:
        if not rows:
            continue
        table = entry["table"]
        key = entry["primary_key"]
        ids = [row[key] for row in rows]
        marks = ", ".join(f":id_{index}" for index in range(len(ids)))
        params = {f"id_{index}": value for index, value in enumerate(ids)}
        found = conn.execute(text(f"SELECT {key} FROM {table} WHERE {key} IN ({marks})"), params).scalars().all()
        if found:
            collisions.append(f"{table}: {', '.join(map(str, found))}")
    if collisions:
        raise RuntimeError("Target already contains Batch 2 primary keys. STOP: " + "; ".join(collisions))


def _insert_bundle(conn, bundle):
    inserted = 0
    for entry, rows in bundle:
        if not rows:
            continue
        table = entry["table"]
        columns = list(rows[0])
        placeholders = ", ".join(f":{column}" for column in columns)
        conn.execute(text(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"), rows)
        inserted += len(rows)
    return inserted


def main(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    bundle = _load_bundle(args.input_dir)
    engine = create_engine(args.database_url)
    _validate_target(engine, bundle)
    mode = "EXECUTE" if args.execute else "DRY-RUN"

    print("=" * 72)
    print(f"Batch 2 Whitelist Import ({mode})")
    print("=" * 72)
    print(f"Input: {args.input_dir}")
    print(f"Target: {args.database_url}")
    print("Safety: existing primary keys are a stop condition; no upsert is used.")

    with engine.begin() as conn:
        _assert_no_primary_key_collisions(conn, bundle)
        total = sum(len(rows) for _, rows in bundle)
        for entry, rows in bundle:
            print(f"  {entry['table']}: {len(rows)} row(s)")
        if args.execute:
            inserted = _insert_bundle(conn, bundle)
            print(f"Inserted count: {inserted}")
        else:
            print(f"Candidate count: {total}")
            print("Dry-run only. Re-run with --execute after parity review and backup.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
