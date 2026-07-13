import csv
import json
import sqlite3
import subprocess
import sys
from pathlib import Path


PROPERTY_IDS = (1, 2, 3, 4, 5, 6, 21, 22)


def _run(root: Path, script_name: str, *args: str):
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "real_import" / script_name), *args],
        capture_output=True,
        text=True,
        cwd=root,
    )


def _create_legacy_source(source_db: Path):
    schemas = {
        "landlords": ["id", "name", "phone", "electricity_account", "water_account", "electricity_rate_type", "electricity_rate", "water_rate_type", "water_rate", "notes", "created_at"],
        "properties": ["id", "landlord_id", "name", "address", "total_rooms", "electricity_meter_type", "water_meter_type", "billing_rule", "created_at"],
        "rooms": ["id", "property_id", "room_number", "rent", "deposit", "electricity_meter_id", "water_meter_id", "area_ping", "status", "notes", "created_at"],
        "tenants": ["id", "name", "phone", "id_number", "emergency_contact", "emergency_phone", "notes", "created_at"],
        "contracts": ["id", "tenant_id", "room_id", "start_date", "end_date", "rent", "deposit", "electricity_rate", "water_rate", "status", "notes", "start_electricity_reading", "start_water_reading", "created_at"],
        "monthly_bills": ["id", "contract_id", "year_month", "rent", "electricity_prev", "electricity_curr", "electricity_usage", "electricity_amount", "public_electricity", "water_prev", "water_curr", "water_usage", "water_amount", "other_charges", "other_desc", "previous_balance", "total", "paid", "paid_date", "notes", "created_at"],
        "electricity_meters": ["id", "property_id", "is_main", "meter_number", "room_id", "room_number", "notes", "created_at"],
        "electricity_bills": ["id", "property_id", "meter_id", "period_start", "period_end", "year_month", "prev_reading", "curr_reading", "total_usage", "total_amount", "public_amount", "flow_amount", "calc_method_id", "status", "ocr_raw_text", "notes", "created_at", "created_by"],
        "electricity_readings": ["id", "bill_id", "meter_id", "room_id", "prev_reading", "curr_reading", "usage", "calculated_amount", "confirmed_amount", "notes", "created_at"],
    }
    with sqlite3.connect(source_db) as conn:
        for table, columns in schemas.items():
            definitions = [f"{column} INTEGER" if column == "id" or column.endswith("_id") else f"{column} TEXT" for column in columns]
            conn.execute(f"CREATE TABLE {table} ({', '.join(definitions)})")
        conn.execute("INSERT INTO landlords (id, name) VALUES ('1', 'Owner')")
        for property_id in PROPERTY_IDS:
            conn.execute("INSERT INTO properties (id, landlord_id, name) VALUES (?, '1', ?)", (str(property_id), f"P{property_id}"))
            conn.execute(
                "INSERT INTO rooms (id, property_id, room_number, status) VALUES (?, ?, 'A', 'occupied')",
                (str(property_id), str(property_id)),
            )
            conn.execute("INSERT INTO tenants (id, name) VALUES (?, ?)", (str(property_id), f"T{property_id}"))
            conn.execute(
                "INSERT INTO contracts (id, tenant_id, room_id, start_date, end_date, rent, status) "
                "VALUES (?, ?, ?, '2026-01-01', '2026-12-31', '1000', 'active')",
                (str(property_id), str(property_id), str(property_id)),
            )
            conn.execute(
                "INSERT INTO monthly_bills (id, contract_id, year_month, rent, total, paid) VALUES (?, ?, '202601', '1000', '1000', '0')",
                (str(property_id), str(property_id)),
            )


def _create_target_from_bundle(target_db: Path, bundle_dir: Path):
    manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    with sqlite3.connect(target_db) as conn:
        for entry in manifest["tables"]:
            with (bundle_dir / f"{entry['table']}.csv").open(newline="", encoding="utf-8") as handle:
                columns = next(csv.reader(handle))
            definitions = [f"{column} TEXT" for column in columns]
            definitions[columns.index("id")] = "id TEXT PRIMARY KEY"
            conn.execute(f"CREATE TABLE {entry['table']} ({', '.join(definitions)})")


def test_batch2_whitelist_export_and_incremental_import_round_trip(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source_db = tmp_path / "legacy.db"
    output_dir = tmp_path / "batch2"
    target_db = tmp_path / "target.db"
    _create_legacy_source(source_db)

    dry_export = _run(root, "export_batch2_whitelist.py", "--source-db", str(source_db), "--output-dir", str(output_dir))
    assert dry_export.returncode == 0
    assert "Total rows: 41" in dry_export.stdout
    assert not output_dir.exists()

    export = _run(root, "export_batch2_whitelist.py", "--source-db", str(source_db), "--output-dir", str(output_dir), "--execute")
    assert export.returncode == 0
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["created_at_fallback"] == "1970-01-01 00:00:00"
    _create_target_from_bundle(target_db, output_dir)
    target_url = f"sqlite:///{target_db}"

    dry_import = _run(root, "import_batch2_whitelist.py", "--input-dir", str(output_dir), "--database-url", target_url)
    assert dry_import.returncode == 0
    assert "Candidate count: 41" in dry_import.stdout

    execute = _run(root, "import_batch2_whitelist.py", "--input-dir", str(output_dir), "--database-url", target_url, "--execute")
    assert execute.returncode == 0
    assert "Inserted count: 41" in execute.stdout

    repeat = _run(root, "import_batch2_whitelist.py", "--input-dir", str(output_dir), "--database-url", target_url)
    assert repeat.returncode == 1
    assert "STOP" in repeat.stderr or "STOP" in repeat.stdout
