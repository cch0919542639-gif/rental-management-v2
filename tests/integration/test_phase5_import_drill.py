from datetime import date
from decimal import Decimal
import json
from pathlib import Path
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


def _seed_import_data(database_uri: str):
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
            total=Decimal("1000"),
            paid=False,
        )
        db.session.add(bill)
        db.session.commit()


def _export_source(root: Path, source_uri: str, export_dir: Path):
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "export_sqlite_to_pg.py"),
            "--source-url",
            source_uri,
            "--output-dir",
            str(export_dir),
            "--execute",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        check=True,
    )


def test_import_csv_to_target_dry_run_reports_target_counts(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source_db = tmp_path / "source.db"
    target_db = tmp_path / "target.db"
    export_dir = tmp_path / "export"
    source_uri = f"sqlite:///{source_db}"
    target_uri = f"sqlite:///{target_db}"
    _seed_import_data(source_uri)
    _seed_import_data(target_uri)
    _export_source(root, source_uri, export_dir)

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "import_csv_to_target.py"),
            "--manifest",
            str(export_dir / "manifest.json"),
            "--target-url",
            target_uri,
        ],
        capture_output=True,
        text=True,
        cwd=root,
    )

    assert result.returncode == 1
    assert "is not empty" in result.stderr or "is not empty" in result.stdout


def test_import_csv_to_target_execute_loads_empty_target_and_parity_passes(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source_db = tmp_path / "source.db"
    target_db = tmp_path / "target.db"
    export_dir = tmp_path / "export"
    source_uri = f"sqlite:///{source_db}"
    target_uri = f"sqlite:///{target_db}"
    _seed_import_data(source_uri)

    # Create empty target schema only.
    app = _build_db_app(target_uri)
    with app.app_context():
        db.drop_all()
        db.create_all()

    _export_source(root, source_uri, export_dir)

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "import_csv_to_target.py"),
            "--manifest",
            str(export_dir / "manifest.json"),
            "--target-url",
            target_uri,
            "--execute",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        check=True,
    )
    assert "Import complete." in result.stdout

    parity = subprocess.run(
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
    assert "Result : PASS" in parity.stdout


def test_import_csv_to_target_requires_manifest_file(tmp_path):
    root = Path(__file__).resolve().parents[2]
    target_db = tmp_path / "target.db"
    target_uri = f"sqlite:///{target_db}"

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "import_csv_to_target.py"),
            "--manifest",
            str(tmp_path / "missing-manifest.json"),
            "--target-url",
            target_uri,
        ],
        capture_output=True,
        text=True,
        cwd=root,
    )

    assert result.returncode == 1
    assert "Manifest not found" in result.stderr or "Manifest not found" in result.stdout
