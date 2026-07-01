from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import os
import sqlite3
import subprocess
import sys

from flask import Flask

from app.core.db import db
from app.core.db import init_extensions
from app.models import Contract, Landlord, MonthlyBill, Property, Room, Tenant, User


def _build_db_app(database_uri: str):
    flask_app = Flask(__name__)
    flask_app.config.update(
        SECRET_KEY="test-secret",
        SQLALCHEMY_DATABASE_URI=database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
    )
    init_extensions(flask_app)

    import app.models  # noqa: F401

    return flask_app


def _seed_minimum_export_data(database_uri: str, monthly_bill_total: str = "12000.00"):
    app = _build_db_app(database_uri)
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(username="admin", name="Admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        landlord = Landlord(name="Owner A")
        db.session.add(landlord)
        db.session.flush()

        prop = Property(landlord_id=landlord.id, name="North House")
        db.session.add(prop)
        db.session.flush()

        room = Room(property_id=prop.id, room_number="A01", status="occupied", rent=Decimal("1000"))
        tenant = Tenant(name="Tenant One")
        db.session.add_all([room, tenant])
        db.session.flush()

        contract = Contract(
            tenant_id=tenant.id,
            room_id=room.id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            rent=Decimal("1000"),
            status="active",
        )
        db.session.add(contract)
        db.session.flush()

        bill = MonthlyBill(
            contract_id=contract.id,
            year_month="202606",
            rent=Decimal("1000"),
            total=Decimal(monthly_bill_total),
            paid=False,
        )
        db.session.add(bill)
        db.session.commit()


def test_export_sqlite_to_pg_dry_run_reports_table_counts(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "source.db"
    output_dir = tmp_path / "export"
    database_uri = f"sqlite:///{db_path}"
    _seed_minimum_export_data(database_uri)

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "export_sqlite_to_pg.py"),
            "--source-url",
            database_uri,
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        cwd=root,
        check=True,
    )

    assert "SQLite Export Drill" in result.stdout
    assert "landlords: 1 row(s)" in result.stdout
    assert "monthly_bills: 1 row(s)" in result.stdout
    assert not output_dir.exists()


def test_export_sqlite_to_pg_execute_writes_manifest_and_csv(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "source.db"
    output_dir = tmp_path / "export"
    database_uri = f"sqlite:///{db_path}"
    _seed_minimum_export_data(database_uri)

    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "export_sqlite_to_pg.py"),
            "--source-url",
            database_uri,
            "--output-dir",
            str(output_dir),
            "--execute",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        check=True,
    )

    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_dialect"] == "sqlite"
    assert "monthly_bills" in manifest["table_order"]
    assert (output_dir / "monthly_bills.csv").exists()


def test_verify_row_parity_passes_for_identical_sqlite_databases(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source_db = tmp_path / "source.db"
    target_db = tmp_path / "target.db"
    source_uri = f"sqlite:///{source_db}"
    target_uri = f"sqlite:///{target_db}"
    _seed_minimum_export_data(source_uri)
    _seed_minimum_export_data(target_uri)

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "verify_row_parity.py"),
            "--source-url",
            source_uri,
            "--target-url",
            target_uri,
        ],
        capture_output=True,
        text=True,
        cwd=root,
        check=True,
    )

    assert "Result : PASS" in result.stdout


def test_verify_row_parity_fails_on_count_mismatch(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source_db = tmp_path / "source.db"
    target_db = tmp_path / "target.db"
    source_uri = f"sqlite:///{source_db}"
    target_uri = f"sqlite:///{target_db}"
    _seed_minimum_export_data(source_uri, monthly_bill_total="12000.00")
    _seed_minimum_export_data(target_uri, monthly_bill_total="12000.00")

    conn = sqlite3.connect(target_db)
    try:
        conn.execute("DELETE FROM monthly_bills")
        conn.commit()
    finally:
        conn.close()

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "verify_row_parity.py"),
            "--source-url",
            source_uri,
            "--target-url",
            target_uri,
        ],
        capture_output=True,
        text=True,
        cwd=root,
    )

    assert result.returncode == 1
    assert "monthly_bills: source=1 target=0 [MISMATCH]" in result.stdout
