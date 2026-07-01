"""Read-only production preflight health check."""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def ok(msg: str):
    print(f"  [PASS] {msg}")


def fail(msg: str):
    print(f"  [FAIL] {msg}")


def _build_parser():
    parser = argparse.ArgumentParser(description="Read-only application health check")
    parser.add_argument(
        "--config",
        default="production",
        help="App config profile to load (default: production)",
    )
    return parser


def main() -> int:
    from app import create_app
    from app.core.config import get_runtime_config_issues
    from app.core.db import db

    args = _build_parser().parse_args()
    try:
        app = create_app(args.config)
    except Exception as exc:
        print("=" * 54)
        fail(f"App bootstrap failed: {exc}")
        print("=" * 54)
        return 1

    errors = 0

    print("=" * 54)
    print("  Rental System — Production Preflight Health Check")
    print("=" * 54)
    print(f"  Config Profile: {args.config}")

    # 1. App factory
    try:
        assert app is not None
        ok("Flask app created")
    except Exception as e:
        fail(f"Flask app creation failed: {e}")
        errors += 1

    # 2. Database connection
    with app.app_context():
        try:
            db.engine.connect()
            ok("Database connection OK")
        except Exception as e:
            fail(f"Database connection failed: {e}")
            errors += 1

        # 3. Table presence
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = set(inspector.get_table_names())
        required = {"user", "landlords", "properties", "rooms", "tenants",
                     "contracts", "monthly_bills", "payment_records",
                     "water_bills", "electricity_meters", "electricity_bills",
                     "electricity_readings", "calc_methods", "maintenance_requests"}
        missing = required - tables
        if missing:
            fail(f"Missing tables: {missing}")
            errors += 1
        else:
            ok(f"All {len(required)} required tables present")

        # 4. Seed data presence (admin user)
        from app.models import User
        admin = User.query.filter_by(username="admin").first()
        if admin:
            ok("Admin user found")
        else:
            fail("Admin user not found — run seed_demo_data.py")
            errors += 1

        # 5. Active contracts
        from app.models import Contract
        active = Contract.query.filter_by(status="active").count()
        if active > 0:
            ok(f"{active} active contract(s)")
        else:
            fail("No active contracts found")
            errors += 1

    # 6. Config safety checks (outside app_context)
    config = app.config
    if config.get("SECRET_KEY") and config["SECRET_KEY"] != "change-me-in-production":
        ok("SECRET_KEY is set")
    else:
        fail("SECRET_KEY is using default value — set via environment variable")
        errors += 1

    if config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite:///:memory:"):
        fail("DATABASE_URL is in-memory — not suitable for production")
        errors += 1
    else:
        ok(f"Database: {config['SQLALCHEMY_DATABASE_URI'][:60]}...")

    for issue in get_runtime_config_issues(app):
        if issue["severity"] == "warning":
            print(f"  [WARN] {issue['code']}: {issue['message']}")

    print("=" * 54)
    if errors == 0:
        print("  All checks passed.")
        print("=" * 54)
        return 0
    else:
        print(f"  {errors} check(s) failed — review output above.")
        print("=" * 54)
        return 1


if __name__ == "__main__":
    sys.exit(main())
