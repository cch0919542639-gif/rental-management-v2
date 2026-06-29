from datetime import date
import os
from pathlib import Path
import subprocess
import sys

from flask import Flask

from app.core.db import db
from app.core.db import init_extensions
from app.models import Contract, Landlord, Property, Room, Tenant


def _run_script(script_path: Path):
    return subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=script_path.parents[2],
        check=True,
    )


def _build_db_app(database_uri: str):
    flask_app = Flask(__name__)
    flask_app.config.update(
        SECRET_KEY="test-secret",
        SQLALCHEMY_DATABASE_URI=database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
    )
    init_extensions(flask_app)

    # Populate SQLAlchemy metadata before create_all().
    import app.models  # noqa: F401

    return flask_app


def test_repair_scripts_run_read_only():
    root = Path(__file__).resolve().parents[2]
    scripts = [
        root / "scripts" / "repair" / "year_month_audit.py",
        root / "scripts" / "repair" / "room_status_audit.py",
        root / "scripts" / "repair" / "user_table_audit.py",
        root / "scripts" / "repair" / "contract_expiry_repair.py",
    ]
    for script in scripts:
        result = _run_script(script)
        assert result.returncode == 0
        assert result.stdout.strip()


def test_contract_expiry_repair_execute_updates_expired_contracts(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "repair-execute.db"
    database_uri = f"sqlite:///{db_path}"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_uri
    env["SCRIPT_APP_CONFIG"] = "default"

    app = _build_db_app(database_uri)
    with app.app_context():
        db.drop_all()
        db.create_all()
        landlord = Landlord(name="L1")
        db.session.add(landlord)
        db.session.flush()
        prop = Property(landlord_id=landlord.id, name="P1")
        db.session.add(prop)
        db.session.flush()
        room = Room(property_id=prop.id, room_number="A01", status="occupied")
        tenant = Tenant(name="T1")
        db.session.add_all([room, tenant])
        db.session.flush()
        contract = Contract(
            tenant_id=tenant.id,
            room_id=room.id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            rent=1000,
            status="active",
        )
        db.session.add(contract)
        db.session.commit()
        contract_id = contract.id

    script = root / "scripts" / "repair" / "contract_expiry_repair.py"
    dry_run = subprocess.run(
        [sys.executable, str(script), "--reference-date", "2026-02-01"],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert "Candidate count: 1" in dry_run.stdout
    assert "Dry-run only" in dry_run.stdout

    with app.app_context():
        contract = db.session.get(Contract, contract_id)
        assert contract.status == "active"

    execute = subprocess.run(
        [sys.executable, str(script), "--reference-date", "2026-02-01", "--execute"],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert "Updated count: 1" in execute.stdout

    with app.app_context():
        contract = db.session.get(Contract, contract_id)
        assert contract.status == "expired"


def test_line_webhook_placeholder_returns_501(client, logged_in_client):
    response = client.post("/integrations/line/callback")
    assert response.status_code == 501
    payload = response.get_json()
    assert payload["error"] == "not_implemented"


def test_payment_list_shows_ocr_section_when_present(app, logged_in_client, seeded_data):
    client = logged_in_client
    response = client.post(
        "/payments/create",
        data={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "12000",
            "bank_name": "Bank A",
            "account_number": "123456",
            "account_holder": "Tenant One",
            "transaction_date": "2026-06-05",
            "payer_name": "Tenant One",
            "transaction_id": "TXN-OCR-001",
            "status_text": "匯款成功",
            "raw_ocr_text": "OCR TEXT",
            "raw_llm_response": "{\"amount\":12000}",
            "image_path": "uploads/payment-001.jpg",
            "ocr_engine": "placeholder",
            "notes": "ocr evidence test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "OCR 資訊" in text
    assert "uploads/payment-001.jpg" in text
