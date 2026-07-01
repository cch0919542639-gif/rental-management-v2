from datetime import date
from decimal import Decimal
import json
from pathlib import Path
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


def _seed_target_prep_data(database_uri: str):
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


def test_prepare_target_db_dry_run_reports_missing_tables(tmp_path):
    root = Path(__file__).resolve().parents[2]
    target_db = tmp_path / "target.db"
    target_uri = f"sqlite:///{target_db}"

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "prepare_target_db.py"),
            "--target-url",
            target_uri,
        ],
        capture_output=True,
        text=True,
        cwd=root,
        check=True,
    )

    assert "Target DB Preparation" in result.stdout
    assert "Missing tables" in result.stdout
    assert "Dry-run only." in result.stdout


def test_prepare_target_db_execute_creates_schema(tmp_path):
    root = Path(__file__).resolve().parents[2]
    target_db = tmp_path / "target.db"
    target_uri = f"sqlite:///{target_db}"

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "prepare_target_db.py"),
            "--target-url",
            target_uri,
            "--execute",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        check=True,
    )

    assert "Target schema prepared." in result.stdout


def test_prepare_target_db_blocks_nonempty_target_without_override(tmp_path):
    root = Path(__file__).resolve().parents[2]
    target_db = tmp_path / "target.db"
    target_uri = f"sqlite:///{target_db}"
    _seed_target_prep_data(target_uri)

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "prepare_target_db.py"),
            "--target-url",
            target_uri,
            "--execute",
        ],
        capture_output=True,
        text=True,
        cwd=root,
    )

    assert result.returncode == 1
    assert "refusing to proceed without --allow-nonempty" in result.stderr or "refusing to proceed without --allow-nonempty" in result.stdout


def test_write_rehearsal_evidence_writes_json_bundle(tmp_path):
    root = Path(__file__).resolve().parents[2]
    manifest_path = tmp_path / "manifest.json"
    parity_log = tmp_path / "parity.log"
    checklist_log = tmp_path / "checklist.log"
    output_dir = tmp_path / "evidence"
    manifest_path.write_text(
        json.dumps({"tables": [{"table_name": "monthly_bills", "row_count": 1}, {"table_name": "contracts", "row_count": 1}]}),
        encoding="utf-8",
    )
    parity_log.write_text("Result : PASS\n", encoding="utf-8")
    checklist_log.write_text("[PASS] baseline-marker\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "write_rehearsal_evidence.py"),
            "--label",
            "rehearsal-01",
            "--manifest",
            str(manifest_path),
            "--parity-log",
            str(parity_log),
            "--checklist-log",
            str(checklist_log),
            "--output-dir",
            str(output_dir),
            "--execute",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        check=True,
    )

    evidence_path = output_dir / "rehearsal-01.json"
    assert evidence_path.exists()
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["manifest_table_count"] == 2
    assert evidence["parity_pass"] is True
    assert evidence["checklist_has_fail"] is False
    assert "Wrote evidence bundle" in result.stdout
