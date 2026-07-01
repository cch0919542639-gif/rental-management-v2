from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.db import db
from scripts.migration._common import build_script_app
from scripts.migration._registry import (
    MigrationContext,
    discover_migrations,
    ensure_migration_log_table,
    get_applied_migration_ids,
    record_migration,
)


def _build_parser():
    parser = argparse.ArgumentParser(description="Run versioned migration scripts with dry-run-first behavior.")
    parser.add_argument("--list", action="store_true", help="List known migrations and their status")
    parser.add_argument("--execute", action="store_true", help="Apply pending or selected migrations")
    parser.add_argument("--id", dest="migration_id", help="Run only one migration by MIGRATION_ID")
    parser.add_argument(
        "--allow-bridge",
        action="store_true",
        help="Required to execute the Alembic bridge migration after explicit review approval",
    )
    return parser


def _select_migrations(all_migrations, selected_id: str | None):
    if not selected_id:
        return all_migrations
    selected = [item for item in all_migrations if item.migration_id == selected_id]
    if not selected:
        raise SystemExit(f"Unknown migration id: {selected_id}")
    return selected


def _is_bridge_migration(migration_id: str) -> bool:
    return migration_id.endswith("_alembic_bridge")


def _assert_bridge_execute_allowed(selected, all_migrations, applied_ids: set[str], allow_bridge: bool, execute: bool):
    if not execute:
        return

    selected_bridge = [migration for migration in selected if _is_bridge_migration(migration.migration_id)]
    if not selected_bridge:
        return

    if not allow_bridge:
        raise SystemExit(
            "Alembic bridge execution is gated. Re-run with --allow-bridge only after the Phase 5B gate is approved."
        )

    earliest_bridge_index = min(all_migrations.index(migration) for migration in selected_bridge)
    pending_before_bridge = [
        migration.migration_id
        for migration in all_migrations[:earliest_bridge_index]
        if migration.migration_id not in applied_ids
    ]
    if pending_before_bridge:
        pending_list = ", ".join(pending_before_bridge)
        raise SystemExit(
            "Alembic bridge requires all earlier migrations to be applied first. "
            f"Pending before bridge: {pending_list}"
        )


def main(argv: list[str]):
    args = _build_parser().parse_args(argv)
    app = build_script_app()
    all_migrations = discover_migrations(ROOT)

    with app.app_context():
        ensure_migration_log_table(db)
        applied_ids = get_applied_migration_ids(db)
        selected = _select_migrations(all_migrations, args.migration_id)
        _assert_bridge_execute_allowed(selected, all_migrations, applied_ids, args.allow_bridge, args.execute)

        print("=" * 72)
        print("Migration Runner")
        print("=" * 72)

        if args.list:
            for migration in selected:
                status = "applied" if migration.migration_id in applied_ids else "pending"
                print(f"{migration.migration_id} [{status}]")
                print(f"  Desc : {migration.description}")
                print(f"  File : {migration.path.name}")
            print("=" * 72)
            return

        mode = "EXECUTE" if args.execute else "DRY-RUN"
        print(f"Mode: {mode}")
        print("-" * 72)

        for migration in selected:
            already_applied = migration.migration_id in applied_ids
            if already_applied:
                print(f"Skip {migration.migration_id}: already applied")
                continue

            print(f"Run  {migration.migration_id}")
            print(f"Desc {migration.description}")
            context = MigrationContext(app=app, db=db, execute=args.execute)
            result = migration.module.run_migration(context) or {}
            summary = result.get("summary", "No summary provided.")
            print(f"Note {summary}")

            if args.execute:
                record_migration(db, migration)
                print("Applied and recorded.")
            else:
                print("Dry-run only. No migration log written.")
            print("-" * 72)

        print("=" * 72)


if __name__ == "__main__":
    main(sys.argv[1:])
