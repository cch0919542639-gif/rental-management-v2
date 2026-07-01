from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.db_runtime_common import get_db_dialect


def _build_parser():
    parser = argparse.ArgumentParser(description="Read-only PostgreSQL bridge tooling preflight.")
    parser.add_argument("--database-url", help="Override DATABASE_URL for this check")
    parser.add_argument("--pg-dump-bin", default=os.getenv("PG_DUMP_BIN", "pg_dump"))
    parser.add_argument("--psql-bin", default=os.getenv("PSQL_BIN", "psql"))
    parser.add_argument("--skip-binaries", action="store_true", help="Skip PATH checks for pg_dump / psql")
    return parser


def _ok(message: str):
    print(f"  [PASS] {message}")


def _warn(message: str):
    print(f"  [WARN] {message}")


def _fail(message: str):
    print(f"  [FAIL] {message}")


def main() -> int:
    args = _build_parser().parse_args()
    database_url = args.database_url or os.getenv("DATABASE_URL", "")
    errors = 0

    print("=" * 60)
    print("  PostgreSQL Tooling Preflight")
    print("=" * 60)

    if not database_url:
        _fail("DATABASE_URL is not set.")
        errors += 1
    else:
        dialect = get_db_dialect(database_url)
        if dialect not in {"postgresql", "postgres"}:
            _fail(f"DATABASE_URL must be PostgreSQL for Phase 5 bridge. Got: {dialect or 'unknown'}")
            errors += 1
        else:
            _ok(f"DATABASE_URL uses supported dialect: {dialect}")

    alembic_ini = ROOT / "alembic.ini"
    env_py = ROOT / "app" / "migrations" / "env.py"
    bridge_script = ROOT / "scripts" / "migration" / "apply_20260701_000002_alembic_bridge.py"

    if alembic_ini.exists():
        _ok("alembic.ini present")
    else:
        _fail("alembic.ini missing")
        errors += 1

    if env_py.exists():
        _ok("app/migrations/env.py present")
    else:
        _fail("app/migrations/env.py missing")
        errors += 1

    if bridge_script.exists():
        _ok("Alembic bridge migration present")
    else:
        _fail("Alembic bridge migration missing")
        errors += 1

    if os.getenv("SECRET_KEY"):
        _ok("SECRET_KEY present")
    else:
        _warn("SECRET_KEY not set in current shell; production launch will fail until it is set")

    if args.skip_binaries:
        _warn("Binary checks skipped by --skip-binaries")
    else:
        for label, binary in (("pg_dump", args.pg_dump_bin), ("psql", args.psql_bin)):
            resolved = shutil.which(binary)
            if resolved:
                _ok(f"{label} found at {resolved}")
            else:
                _fail(f"{label} not found on PATH (checked: {binary})")
                errors += 1

    print("=" * 60)
    if errors:
        print(f"  PostgreSQL preflight failed with {errors} issue(s).")
        print("=" * 60)
        return 1

    print("  PostgreSQL preflight passed.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
