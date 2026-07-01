"""
Read-only PostgreSQL bridge drill checklist.

Purpose:
  - Validate the minimum preconditions before a Phase 5 bridge rehearsal
  - Confirm migration runner state, environment variables, and optional export artifacts
  - Provide a deterministic operator checklist without changing any database state

Rollback:
  - No rollback needed; this script is read-only.

Verification:
  - Run against the local SQLite baseline and confirm bridge is still pending.
  - Re-run after export drills to confirm manifest detection and migration status.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.core.db import db
from scripts.db_runtime_common import get_database_url, get_db_dialect, is_postgresql_url
from scripts.migration._registry import ensure_migration_log_table, get_applied_migration_ids


BASELINE_ID = "20260701_000001_phase4_baseline_marker"
BRIDGE_ID = "20260701_000002_alembic_bridge"


def _build_parser():
    parser = argparse.ArgumentParser(description="Read-only checklist for the PostgreSQL bridge drill.")
    parser.add_argument("--source-url", help="Override source DATABASE_URL")
    parser.add_argument(
        "--export-dir",
        default="migration_exports",
        help="Optional export directory to inspect for manifest.json",
    )
    return parser


def _ok(label: str, detail: str):
    print(f"[PASS] {label}: {detail}")


def _warn(label: str, detail: str):
    print(f"[WARN] {label}: {detail}")


def _fail(label: str, detail: str):
    print(f"[FAIL] {label}: {detail}")


def main():
    args = _build_parser().parse_args()
    source_url = args.source_url or get_database_url()
    export_dir = Path(args.export_dir)
    app = create_app("default")
    failures = 0

    print("=" * 72)
    print("Phase 5 Bridge Drill Checklist")
    print("=" * 72)
    print(f"Source URL : {source_url}")
    print(f"Dialect    : {get_db_dialect(source_url) or 'unknown'}")
    print(f"Export Dir : {export_dir.resolve()}")
    print("-" * 72)

    if get_db_dialect(source_url) == "sqlite":
        _ok("source-dialect", "SQLite source accepted for bridge rehearsal")
    else:
        _warn("source-dialect", "Source is not SQLite; this is valid only if you are rehearsing on a copied target.")

    if os.getenv("DATABASE_URL") and is_postgresql_url(os.getenv("DATABASE_URL", "")):
        _ok("target-env", "DATABASE_URL points to PostgreSQL in current shell")
    else:
        _warn("target-env", "Current shell DATABASE_URL is not PostgreSQL; bridge rehearsal can still inspect source only")

    with app.app_context():
        ensure_migration_log_table(db)
        applied = get_applied_migration_ids(db)
        if BASELINE_ID in applied:
            _ok("baseline-marker", "Phase 4 baseline marker is applied")
        else:
            _fail("baseline-marker", "Phase 4 baseline marker is missing")
            failures += 1

        if BRIDGE_ID in applied:
            _warn("bridge-marker", "Alembic bridge is already marked applied")
        else:
            _ok("bridge-marker", "Alembic bridge is still pending")

    manifest_path = export_dir / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            table_count = len(manifest.get("tables", []))
            _ok("export-manifest", f"Found manifest.json with {table_count} table entry(ies)")
        except Exception as exc:  # pragma: no cover - defensive output
            _fail("export-manifest", f"manifest.json exists but could not be parsed: {exc}")
            failures += 1
    else:
        _warn("export-manifest", "No manifest.json found; run export_sqlite_to_pg.py --execute before full rehearsal")

    alembic_ini = ROOT / "alembic.ini"
    env_py = ROOT / "app" / "migrations" / "env.py"
    if alembic_ini.exists() and env_py.exists():
        _ok("alembic-scaffold", "alembic.ini and env.py present")
    else:
        _fail("alembic-scaffold", "Alembic scaffold incomplete")
        failures += 1

    print("-" * 72)
    print("Next Steps:")
    print("1. Run export_sqlite_to_pg.py --execute to produce CSV + manifest for rehearsal.")
    print("2. Run verify_row_parity.py after loading the target database copy.")
    print("3. Execute run_migrations.py --list and confirm bridge remains pending until the cutover gate.")
    print("4. Only run the bridge with --allow-bridge after explicit approval.")
    print("=" * 72)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
