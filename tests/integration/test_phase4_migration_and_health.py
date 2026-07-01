from datetime import date
from pathlib import Path
import os
import sqlite3
import subprocess
import sys

from flask import Flask

from app.core.db import db
from app.core.db import init_extensions
from app.models import Contract, Landlord, Property, Room, Tenant, User


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


def _seed_minimum_launch_data(database_uri: str):
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

        room = Room(property_id=prop.id, room_number="A01", status="occupied", rent=1000)
        tenant = Tenant(name="Tenant One")
        db.session.add_all([room, tenant])
        db.session.flush()

        contract = Contract(
            tenant_id=tenant.id,
            room_id=room.id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            rent=1000,
            status="active",
        )
        db.session.add(contract)
        db.session.commit()


def test_migration_runner_lists_and_records_baseline(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "migration-runner.db"
    database_uri = f"sqlite:///{db_path}"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_uri
    env["SCRIPT_APP_CONFIG"] = "default"
    env["SECRET_KEY"] = "test-secret"

    list_result = subprocess.run(
        [sys.executable, str(root / "scripts" / "migration" / "run_migrations.py"), "--list"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=root,
        env=env,
        check=True,
    )
    assert "20260701_000001_phase4_baseline_marker [pending]" in list_result.stdout

    execute_result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "migration" / "run_migrations.py"),
            "--execute",
            "--id",
            "20260701_000001_phase4_baseline_marker",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=root,
        env=env,
        check=True,
    )
    assert "Applied and recorded." in execute_result.stdout

    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT migration_id FROM schema_migration_log WHERE migration_id = ?",
            ("20260701_000001_phase4_baseline_marker",),
        ).fetchone()
    finally:
        conn.close()
    assert row is not None


def test_health_check_passes_with_seeded_database(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "health-check.db"
    database_uri = f"sqlite:///{db_path}"
    _seed_minimum_launch_data(database_uri)

    env = os.environ.copy()
    env["DATABASE_URL"] = database_uri
    env["SECRET_KEY"] = "phase4-health-secret"

    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "health_check.py"), "--config", "production"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=root,
        env=env,
        check=True,
    )
    assert "All checks passed." in result.stdout
    assert "Admin user found" in result.stdout
