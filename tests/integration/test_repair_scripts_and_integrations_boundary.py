from datetime import date
import base64
import hashlib
import hmac
import os
from pathlib import Path
import subprocess
import sys

from flask import Flask
from sqlalchemy import text

from app.core.db import db
from app.core.db import init_extensions
from app.models import Contract, Landlord, MonthlyBill, Property, Room, Tenant


def _run_script(script_path: Path, *, env=None):
    return subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=script_path.parents[2],
        env=env,
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


def test_repair_scripts_run_read_only(tmp_path):
    root = Path(__file__).resolve().parents[2]
    database_uri = f"sqlite:///{tmp_path / 'repair-read-only.db'}"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_uri
    env["SCRIPT_APP_CONFIG"] = "default"
    app = _build_db_app(database_uri)
    with app.app_context():
        db.drop_all()
        db.create_all()
    scripts = [
        root / "scripts" / "repair" / "year_month_audit.py",
        root / "scripts" / "repair" / "room_status_audit.py",
        root / "scripts" / "repair" / "user_table_audit.py",
        root / "scripts" / "repair" / "contract_expiry_repair.py",
        root / "scripts" / "repair" / "monthly_bill_paid_null_repair.py",
    ]
    for script in scripts:
        result = _run_script(script, env=env)
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


def test_monthly_bill_paid_null_repair_normalizes_null_flags(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "paid-null-repair.db"
    default_db_path = tmp_path / "wrong-default.db"
    database_uri = f"sqlite:///{db_path}"
    default_database_uri = f"sqlite:///{default_db_path}"
    env = os.environ.copy()
    env["DATABASE_URL"] = default_database_uri
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
            end_date=date(2026, 12, 31),
            rent=1000,
            status="active",
        )
        db.session.add(contract)
        db.session.flush()
        bill = MonthlyBill(contract_id=contract.id, year_month="202606", rent=1000, total=1000, paid=None)
        db.session.add(bill)
        db.session.commit()
        bill_id = bill.id
        db.session.execute(text("UPDATE monthly_bills SET paid = NULL WHERE id = :bill_id"), {"bill_id": bill_id})
        db.session.commit()

    default_app = _build_db_app(default_database_uri)
    with default_app.app_context():
        db.drop_all()
        db.create_all()

    script = root / "scripts" / "repair" / "monthly_bill_paid_null_repair.py"
    dry_run = subprocess.run(
        [sys.executable, str(script), "--database-url", database_uri],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert database_uri in dry_run.stdout
    assert "Candidate count: 1" in dry_run.stdout
    assert "Dry-run only" in dry_run.stdout

    with app.app_context():
        bill = db.session.get(MonthlyBill, bill_id)
        assert bill.paid is None

    execute = subprocess.run(
        [sys.executable, str(script), "--database-url", database_uri, "--execute"],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert "Updated count: 1" in execute.stdout

    with app.app_context():
        bill = db.session.get(MonthlyBill, bill_id)
        assert bill.paid is False


def test_monthly_bill_previous_balance_repair_recalculates_total(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "previous-balance-repair.db"
    database_uri = f"sqlite:///{db_path}"
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///:memory:"
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
            end_date=date(2026, 12, 31),
            rent=4465,
            status="active",
        )
        db.session.add(contract)
        db.session.flush()
        bill = MonthlyBill(
            contract_id=contract.id,
            year_month="202606",
            rent=4465,
            other_charges=198,
            total=4663,
            paid=False,
        )
        db.session.add(bill)
        db.session.commit()
        bill_id = bill.id

    script = root / "scripts" / "repair" / "monthly_bill_previous_balance_repair.py"
    dry_run = subprocess.run(
        [
            sys.executable,
            str(script),
            "--database-url",
            database_uri,
            "--bill-id",
            str(bill_id),
            "--amount",
            "25047",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert "Total: 4,663 -> 29,710" in dry_run.stdout

    execute = subprocess.run(
        [
            sys.executable,
            str(script),
            "--database-url",
            database_uri,
            "--bill-id",
            str(bill_id),
            "--amount",
            "25047",
            "--execute",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert "Updated count: 1" in execute.stdout

    with app.app_context():
        bill = db.session.get(MonthlyBill, bill_id)
        assert float(bill.previous_balance) == 25047.0
        assert float(bill.total) == 29710.0


def _line_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def test_line_webhook_returns_501_without_secret(client, logged_in_client):
    response = client.post("/integrations/line/callback")
    assert response.status_code == 501
    payload = response.get_json()
    assert payload["error"] == "not_configured"


def test_line_webhook_rejects_invalid_signature(app, client, logged_in_client):
    app.config["LINE_CHANNEL_SECRET"] = "test-line-secret"
    response = client.post(
        "/integrations/line/callback",
        data='{"events":[]}',
        headers={"Content-Type": "application/json", "X-Line-Signature": "bad-signature"},
    )
    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "invalid_signature"


def test_line_webhook_accepts_valid_signed_payload(app, client, logged_in_client):
    app.config["LINE_CHANNEL_SECRET"] = "test-line-secret"
    app.config["LINE_CHANNEL_ACCESS_TOKEN"] = "token-123"
    body = (
        '{"events":[{"type":"message","replyToken":"r1","source":{"type":"user","userId":"U123"},'
        '"message":{"id":"m1","type":"image"}}]}'
    ).encode("utf-8")
    signature = _line_signature(app.config["LINE_CHANNEL_SECRET"], body)
    response = client.post(
        "/integrations/line/callback",
        data=body,
        headers={"Content-Type": "application/json", "X-Line-Signature": signature},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "accepted"
    assert payload["event_count"] == 1
    assert payload["reply_capable"] is True
    assert payload["events"][0]["message_type"] == "image"
    assert payload["events"][0]["user_id"] == "U123"


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
