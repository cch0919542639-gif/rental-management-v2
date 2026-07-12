"""Export only the approved Batch 2 records from the legacy SQLite database.

The source database is never modified.  Dry-run prints the selected row counts;
``--execute`` writes a self-contained CSV bundle and manifest.  The exporter
keeps only the fields supported by the rebuild schema and leaves policy codes
empty for the subsequent guarded policy-assignment step.
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = Path(r"D:\rental\rental.db")
DEFAULT_OUTPUT = PROJECT_ROOT / "real_import" / "batch2"
PROPERTY_IDS = (1, 2, 3, 4, 5, 6, 21, 22)

TABLE_COLUMNS = {
    "landlords": (
        "id", "name", "phone", "electricity_account", "water_account",
        "electricity_rate_type", "electricity_rate", "water_rate_type", "water_rate", "notes", "created_at",
    ),
    "properties": (
        "id", "landlord_id", "name", "address", "total_rooms", "electricity_meter_type",
        "water_meter_type", "billing_rule", "electricity_policy_code", "water_policy_code", "created_at",
    ),
    "rooms": (
        "id", "property_id", "room_number", "rent", "deposit", "electricity_meter_id", "water_meter_id",
        "area_ping", "status", "electricity_policy_code", "water_policy_code", "notes", "created_at",
    ),
    "tenants": (
        "id", "name", "phone", "id_number", "emergency_contact", "emergency_phone", "notes", "created_at",
    ),
    "contracts": (
        "id", "tenant_id", "room_id", "start_date", "end_date", "rent", "deposit", "electricity_rate",
        "water_rate", "status", "notes", "start_electricity_reading", "start_water_reading", "created_at",
    ),
    "monthly_bills": (
        "id", "contract_id", "year_month", "rent", "electricity_prev", "electricity_curr", "electricity_usage",
        "electricity_amount", "public_electricity", "water_prev", "water_curr", "water_usage", "water_amount",
        "other_charges", "other_desc", "total", "paid", "paid_date", "notes", "created_at",
    ),
    "electricity_meters": (
        "id", "property_id", "is_main", "meter_number", "room_id", "room_number", "notes", "created_at",
    ),
    "electricity_bills": (
        "id", "property_id", "meter_id", "period_start", "period_end", "year_month", "prev_reading",
        "curr_reading", "total_usage", "total_amount", "public_amount", "flow_amount", "calc_method_id", "status",
        "ocr_raw_text", "notes", "created_at", "created_by",
    ),
    "electricity_readings": (
        "id", "bill_id", "meter_id", "room_id", "prev_reading", "curr_reading", "usage", "calculated_amount",
        "confirmed_amount", "notes", "created_at",
    ),
}

IMPORT_ORDER = tuple(TABLE_COLUMNS)


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first Batch 2 legacy whitelist exporter")
    parser.add_argument("--source-db", type=Path, default=DEFAULT_SOURCE, help="Legacy SQLite database path")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="CSV bundle output directory")
    parser.add_argument("--execute", action="store_true", help="Write CSV files and manifest")
    return parser


def _placeholders(values):
    return ", ".join("?" for _ in values)


def _fetch(conn, sql, params=()):
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def _table_columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def _normalized_rows(conn, table, rows):
    available = _table_columns(conn, table)
    output = []
    for row in rows:
        output.append({column: row.get(column) if column in available else None for column in TABLE_COLUMNS[table]})
    return output


def _collect_bundle(conn):
    property_marks = _placeholders(PROPERTY_IDS)
    properties = _fetch(conn, f"SELECT * FROM properties WHERE id IN ({property_marks}) ORDER BY id", PROPERTY_IDS)
    actual_property_ids = {row["id"] for row in properties}
    missing = sorted(set(PROPERTY_IDS) - actual_property_ids)
    if missing:
        raise RuntimeError(f"Legacy source is missing approved property IDs: {', '.join(map(str, missing))}")

    landlord_ids = sorted({row["landlord_id"] for row in properties})
    rooms = _fetch(conn, f"SELECT * FROM rooms WHERE property_id IN ({property_marks}) ORDER BY id", PROPERTY_IDS)
    room_ids = [row["id"] for row in rooms]
    contracts = _fetch(
        conn,
        f"SELECT * FROM contracts WHERE room_id IN ({_placeholders(room_ids)}) ORDER BY id",
        room_ids,
    )
    contract_ids = [row["id"] for row in contracts]
    tenant_ids = sorted({row["tenant_id"] for row in contracts})
    electricity_bills = _fetch(
        conn,
        f"SELECT * FROM electricity_bills WHERE property_id IN ({property_marks}) ORDER BY id",
        PROPERTY_IDS,
    )
    bill_ids = [row["id"] for row in electricity_bills]

    raw = {
        "landlords": _fetch(conn, f"SELECT * FROM landlords WHERE id IN ({_placeholders(landlord_ids)}) ORDER BY id", landlord_ids),
        "properties": properties,
        "rooms": rooms,
        "tenants": _fetch(conn, f"SELECT * FROM tenants WHERE id IN ({_placeholders(tenant_ids)}) ORDER BY id", tenant_ids),
        "contracts": contracts,
        "monthly_bills": _fetch(
            conn,
            f"SELECT * FROM monthly_bills WHERE contract_id IN ({_placeholders(contract_ids)}) ORDER BY id",
            contract_ids,
        ),
        "electricity_meters": _fetch(
            conn,
            f"SELECT * FROM electricity_meters WHERE property_id IN ({property_marks}) ORDER BY id",
            PROPERTY_IDS,
        ),
        "electricity_bills": electricity_bills,
        "electricity_readings": _fetch(
            conn,
            f"SELECT * FROM electricity_readings WHERE bill_id IN ({_placeholders(bill_ids)}) ORDER BY id",
            bill_ids,
        ) if bill_ids else [],
    }
    return {table: _normalized_rows(conn, table, rows) for table, rows in raw.items()}


def _validate_bundle(bundle):
    by_table = {table: {row["id"] for row in rows} for table, rows in bundle.items() if rows and "id" in rows[0]}
    checks = (
        ("properties", "landlord_id", "landlords"),
        ("rooms", "property_id", "properties"),
        ("contracts", "tenant_id", "tenants"),
        ("contracts", "room_id", "rooms"),
        ("monthly_bills", "contract_id", "contracts"),
        ("electricity_meters", "property_id", "properties"),
        ("electricity_bills", "property_id", "properties"),
        ("electricity_readings", "bill_id", "electricity_bills"),
        ("electricity_readings", "meter_id", "electricity_meters"),
    )
    failures = []
    for table, field, parent in checks:
        parent_ids = by_table.get(parent, set())
        invalid = sorted({row[field] for row in bundle[table] if row.get(field) is not None and row[field] not in parent_ids})
        if invalid:
            failures.append(f"{table}.{field} references missing {parent} IDs: {invalid}")
    if failures:
        raise RuntimeError("; ".join(failures))


def _write_bundle(output_dir, bundle, source_db):
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(f"Output directory is not empty: {output_dir}. Choose a new directory; do not overwrite evidence.")
    output_dir.mkdir(parents=True, exist_ok=True)
    tables = []
    for order, table in enumerate(IMPORT_ORDER, start=1):
        rows = bundle[table]
        path = output_dir / f"{table}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=TABLE_COLUMNS[table])
            writer.writeheader()
            writer.writerows(rows)
        tables.append({"table": table, "primary_key": "id", "order": order, "rows": len(rows)})
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "batch": "batch2",
                "approved_property_ids": list(PROPERTY_IDS),
                "source_db": str(source_db),
                "tables": tables,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    if not args.source_db.is_file():
        raise SystemExit(f"Legacy source database not found: {args.source_db}")
    with sqlite3.connect(args.source_db) as conn:
        conn.row_factory = sqlite3.Row
        bundle = _collect_bundle(conn)
    _validate_bundle(bundle)

    print("=" * 72)
    print(f"Batch 2 Whitelist Export ({'EXECUTE' if args.execute else 'DRY-RUN'})")
    print("=" * 72)
    print(f"Source: {args.source_db}")
    print("Approved properties: " + ", ".join(map(str, PROPERTY_IDS)))
    total = 0
    for table in IMPORT_ORDER:
        count = len(bundle[table])
        total += count
        print(f"  {table}: {count}")
    print(f"Total rows: {total}")
    if args.execute:
        _write_bundle(args.output_dir, bundle, args.source_db)
        print(f"Written: {args.output_dir}")
    else:
        print("Dry-run only. Re-run with --execute to write the CSV bundle.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
