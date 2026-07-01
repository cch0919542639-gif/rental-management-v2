from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import os
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


def _seed_checklist_data(database_uri: str):
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


def test_bridge_drill_checklist_reports_pending_bridge(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "checklist.db"
    database_uri = f"sqlite:///{db_path}"
    _seed_checklist_data(database_uri)

    env = os.environ.copy()
    env["DATABASE_URL"] = database_uri
    env["SCRIPT_APP_CONFIG"] = "default"
    env["SECRET_KEY"] = "test-secret"

    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "run_migrations.py"),
            "--execute",
            "--id",
            "20260701_000001_phase4_baseline_marker",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "bridge_drill_checklist.py"),
            "--source-url",
            database_uri,
            "--export-dir",
            str(tmp_path / "missing-export"),
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )

    assert "Phase 5 Bridge Drill Checklist" in result.stdout
    assert "[PASS] baseline-marker" in result.stdout
    assert "[PASS] bridge-marker: Alembic bridge is still pending" in result.stdout
    assert "[WARN] export-manifest" in result.stdout


def test_bridge_drill_checklist_detects_manifest(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "checklist.db"
    export_dir = tmp_path / "export"
    database_uri = f"sqlite:///{db_path}"
    _seed_checklist_data(database_uri)
    export_dir.mkdir()
    (export_dir / "manifest.json").write_text(
        json.dumps({"tables": [{"table_name": "monthly_bills", "row_count": 1}]}),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["DATABASE_URL"] = database_uri
    env["SCRIPT_APP_CONFIG"] = "default"
    env["SECRET_KEY"] = "test-secret"

    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "run_migrations.py"),
            "--execute",
            "--id",
            "20260701_000001_phase4_baseline_marker",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "bridge_drill_checklist.py"),
            "--source-url",
            database_uri,
            "--export-dir",
            str(export_dir),
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )

    assert "[PASS] export-manifest" in result.stdout
