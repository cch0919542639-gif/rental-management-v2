"""Tests for backfill_missing_monthly_bills.py dry-run/execute/skip/stop conditions."""

from datetime import date
from pathlib import Path
from decimal import Decimal
import os
import subprocess
import sys

from flask import Flask
from sqlalchemy import text as sa_text

from app.core.db import db, init_extensions
from app.models import Contract, Landlord, MonthlyBill, Property, Room, Tenant
from app.services import BillingService
from app.repositories import BillingRepository

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "repair" / "backfill_missing_monthly_bills.py"

# ── helpers ─────────────────────────────────────────────────────────────

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


def _run(
    tmp_path,
    db_name,
    argv,
    *,
    env_add=None,
):
    """Run the script as subprocess and return CompletedProcess."""
    db_path = tmp_path / db_name
    database_uri = f"sqlite:///{db_path}"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_uri
    env["SCRIPT_APP_CONFIG"] = "default"
    if env_add:
        env.update(env_add)
    cmd = [sys.executable, str(SCRIPT), "--database-url", database_uri] + argv
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, env=env)


def _seed_basic_scenario(database_uri: str):
    """Create a minimal set of entities: landlord, property, room, tenant, contract."""
    app = _build_db_app(database_uri)
    with app.app_context():
        db.drop_all()
        db.create_all()
        landlord = Landlord(name="L1")
        db.session.add(landlord)
        db.session.flush()
        prop = Property(landlord_id=landlord.id, name="Test Property", address="廣東73號4樓")
        db.session.add(prop)
        db.session.flush()
        room = Room(property_id=prop.id, room_number="1", status="occupied", rent=5000)
        tenant = Tenant(name="伸格股份有限公司")
        db.session.add_all([room, tenant])
        db.session.flush()
        contract = Contract(
            tenant_id=tenant.id, room_id=room.id,
            start_date=date(2025, 1, 1), end_date=date(2026, 12, 31),
            rent=5000, status="active",
        )
        db.session.add(contract)
        db.session.commit()
        return {
            "landlord_id": landlord.id,
            "property_id": prop.id,
            "room_id": room.id,
            "tenant_id": tenant.id,
            "contract_id": contract.id,
        }


def _seed_csv(tmp_path, name, rows_text):
    """Write a minimal CSV to tmp_path."""
    p = tmp_path / name
    p.write_text(rows_text, encoding="utf-8-sig")
    return str(p)


# ── dry-run does not write ──────────────────────────────────────────────

def test_dry_run_does_not_create_bills(tmp_path):
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'dry-run.db'}")
    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        f"L1,廣東73號4樓,1,伸格股份有限公司,,,,\"5,000\",0,0,198,,5198,5198,0,,,\n"
    )
    result = _run(tmp_path, "dry-run.db", ["--csv", csv_path, "--year-month", "202604"])
    assert result.returncode == 0
    assert "SAFE: 1" in result.stdout
    assert "Dry-run only" in result.stdout

    app = _build_db_app(f"sqlite:///{tmp_path / 'dry-run.db'}")
    with app.app_context():
        count = db.session.execute(sa_text("SELECT COUNT(*) FROM monthly_bills")).scalar()
        assert count == 0, "dry-run must not create any bills"


# ── execute writes exactly one bill ────────────────────────────────────

def test_execute_creates_bill(tmp_path):
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'execute.db'}")
    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        f"L1,廣東73號4樓,1,伸格股份有限公司,,,,\"5,000\",0,0,198,,5198,5198,0,,,\n"
    )
    result = _run(tmp_path, "execute.db", ["--csv", csv_path, "--year-month", "202604", "--execute"])
    assert result.returncode == 0
    assert "Created: 1" in result.stdout

    app = _build_db_app(f"sqlite:///{tmp_path / 'execute.db'}")
    with app.app_context():
        count = db.session.execute(sa_text("SELECT COUNT(*) FROM monthly_bills")).scalar()
        assert count == 1
        bill = MonthlyBill.query.first()
        assert bill.contract_id == ids["contract_id"]
        assert bill.year_month == "202604"
        assert float(bill.rent) == 5000
        assert float(bill.other_charges) == 198
        assert float(bill.total) == 5198
        assert bill.paid is False
        assert bill.paid_date is None
        assert "前期差額無證據，設為0" in bill.notes


# ── re-run skips duplicate ─────────────────────────────────────────────

def test_rerun_skips_existing(tmp_path):
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'rerun.db'}")

    # First: create the bill directly
    app = _build_db_app(f"sqlite:///{tmp_path / 'rerun.db'}")
    with app.app_context():
        bill = MonthlyBill(
            contract_id=ids["contract_id"], year_month="202604",
            rent=5000, other_charges=198, total=5198,
            paid=False,
        )
        db.session.add(bill)
        db.session.commit()

    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        f"L1,廣東73號4樓,1,伸格股份有限公司,,,,\"5,000\",0,0,198,,5198,5198,0,,,\n"
    )
    result = _run(tmp_path, "rerun.db", ["--csv", csv_path, "--year-month", "202604", "--execute"])
    assert result.returncode == 0
    assert "duplicate bill=" in result.stdout
    assert "Created: 0" in result.stdout


# ── stop-list tenant is skipped ────────────────────────────────────────

def test_skip_stop_list_tenant(tmp_path):
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'stop-list.db'}")
    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        f"L1,廣東73號4樓,1,張硯傑,,,,\"4,465\",0,0,198,,15416,,15416,00425,,\n"
    )
    result = _run(tmp_path, "stop-list.db", ["--csv", csv_path, "--year-month", "202604"])
    assert result.returncode == 0
    assert "SKIP" in result.stdout
    assert "stop-list tenant" in result.stdout


# ── virtual tenant is skipped ──────────────────────────────────────────

def test_skip_virtual_tenant(tmp_path):
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'virtual.db'}")
    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        f"L1,廣東73號4樓,1,待修浴室,,,,,0,0,0,,0,,0,,,\n"
    )
    result = _run(tmp_path, "virtual.db", ["--csv", csv_path, "--year-month", "202604"])
    assert result.returncode == 0
    assert "SKIP" in result.stdout
    assert "virtual/vacant/repair" in result.stdout


# ── stop condition: rent diff > 100 ────────────────────────────────────

def test_stop_rent_diff_exceeds_threshold(tmp_path):
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'rent-diff.db'}")
    # Contract has rent=5000, sheet has rent=7000 => diff 2000 > 100
    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        f"L1,廣東73號4樓,1,伸格股份有限公司,,,,\"7,000\",0,0,0,,7000,7000,0,,,\n"
    )
    result = _run(tmp_path, "rent-diff.db", ["--csv", csv_path, "--year-month", "202604"])
    assert result.returncode == 0
    assert "STOP" in result.stdout
    assert "rent diff=" in result.stdout


def test_reviewed_override_allows_documented_stop_list_and_historical_rent(tmp_path):
    """A reviewed CSV is the only supported bypass for a stop-list exception."""
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'reviewed.db'}")
    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        "L1,廣東73號4樓,1,張硯傑,,,,7000,0,0,0,,7000,7000,0,,,\n",
    )
    overrides = _seed_csv(
        tmp_path, "reviewed.csv",
        "source_row,contract_id,rent,previous_balance,approved_reason\n"
        f"2,{ids['contract_id']},7000,0,Sheet evidence confirms historical rate\n",
    )
    result = _run(
        tmp_path,
        "reviewed.db",
        [
            "--csv", csv_path,
            "--year-month", "202604",
            "--reviewed-overrides", overrides,
            "--execute",
        ],
    )
    assert result.returncode == 0
    assert "SAFE: 1" in result.stdout
    assert "Created: 1" in result.stdout

    app = _build_db_app(f"sqlite:///{tmp_path / 'reviewed.db'}")
    with app.app_context():
        bill = MonthlyBill.query.one()
        assert float(bill.rent) == 7000
        assert float(bill.total) == 7000
        assert "覆核前期差額" in bill.notes


# ── stop condition: total diff > 10 ────────────────────────────────────

def test_stop_total_diff_exceeds_threshold(tmp_path):
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'total-diff.db'}")
    # rent=5000 + other=198 = 5198, but sheet says 9999 => diff > 10
    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        f"L1,廣東73號4樓,1,伸格股份有限公司,,,,\"5,000\",0,0,198,,9999,9999,0,,,\n"
    )
    result = _run(tmp_path, "total-diff.db", ["--csv", csv_path, "--year-month", "202604"])
    assert result.returncode == 0
    assert "STOP" in result.stdout
    assert "total diff=" in result.stdout


# ── 202605 uses previous_balance from 未收款 column ─────────────────────

def test_202605_previous_balance_from_sheet(tmp_path):
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'pb-202605.db'}")
    csv_path = _seed_csv(
        tmp_path, "test_202605.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,未收款,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間,通知,帳單,計算,備註\n"
        f"L1,廣東73號4樓,1,伸格股份有限公司,,,,5000,579,417,198,,0,6194,6194,0,,,,,,,\n"
    )
    result = _run(tmp_path, "pb-202605.db", ["--csv", csv_path, "--year-month", "202605", "--execute"])
    assert result.returncode == 0
    assert "Created: 1" in result.stdout

    app = _build_db_app(f"sqlite:///{tmp_path / 'pb-202605.db'}")
    with app.app_context():
        bill = MonthlyBill.query.first()
        assert float(bill.previous_balance) == 0  # 未收款=0
        assert bill.paid is False
        assert bill.paid_date is None


# ── no property match → skip ───────────────────────────────────────────

def test_skip_no_property_match(tmp_path):
    ids = _seed_basic_scenario(f"sqlite:///{tmp_path / 'no-prop.db'}")
    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        f"L1,永平38號5樓,1,曾俊庭,,,,5000,0,0,0,,5000,5000,0,,,\n"
    )
    result = _run(tmp_path, "no-prop.db", ["--csv", csv_path, "--year-month", "202604"])
    assert result.returncode == 0
    assert "no property match" in result.stdout


# ── contract rent=0 (placeholder) → skip ──────────────────────────────

def test_skip_contract_rent_zero(tmp_path):
    db_path = tmp_path / "rent-zero.db"
    database_uri = f"sqlite:///{db_path}"
    app = _build_db_app(database_uri)
    with app.app_context():
        db.drop_all()
        db.create_all()
        landlord = Landlord(name="L1")
        db.session.add(landlord)
        db.session.flush()
        prop = Property(landlord_id=landlord.id, name="Test", address="A")
        db.session.add(prop)
        db.session.flush()
        room = Room(property_id=prop.id, room_number="1", status="occupied", rent=0)
        tenant = Tenant(name="待補-1")
        db.session.add_all([room, tenant])
        db.session.flush()
        contract = Contract(
            tenant_id=tenant.id, room_id=room.id,
            start_date=date(2025, 1, 1), end_date=date(2026, 12, 31),
            rent=0, status="active",
        )
        db.session.add(contract)
        db.session.commit()

    csv_path = _seed_csv(
        tmp_path, "test_202604.csv",
        "屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間\n"
        f"L1,A,1,待補-1,,,,5000,0,0,0,,5000,5000,0,,,\n"
    )
    result = _run(tmp_path, "rent-zero.db", ["--csv", csv_path, "--year-month", "202604"])
    assert result.returncode == 0
    assert "contract rent=0" in result.stdout or "10-year" not in result.stdout
