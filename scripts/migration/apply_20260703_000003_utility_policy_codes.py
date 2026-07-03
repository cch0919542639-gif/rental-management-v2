"""
Add utility policy code columns for property defaults and room overrides.

Purpose:
  - Introduce the minimum structure required by Phase 2 utility policy planning
  - Keep fixed-rate compatibility while blocking dynamic strategy execution until
    a dedicated resolver path is implemented

Rollback:
  - SQLite does not support safe DROP COLUMN in-place for this project.
  - Roll back by restoring the rehearsal/runtime database from backup.

Verification:
  - Run `py -3 .\scripts\migration\run_migrations.py --id 20260703_000003_utility_policy_codes`
  - On execute, confirm the 4 columns exist on `properties` and `rooms`
"""

from sqlalchemy import inspect, text


MIGRATION_ID = "20260703_000003_utility_policy_codes"
DESCRIPTION = "Add utility policy_code columns to properties and rooms for Batch 2 gating."


def _existing_columns(db, table_name: str) -> set[str]:
    inspector = inspect(db.engine)
    if not inspector.has_table(table_name):
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _ensure_column(context, table_name: str, column_name: str):
    existing = _existing_columns(context.db, table_name)
    inspector = inspect(context.db.engine)
    if not inspector.has_table(table_name):
        if context.execute:
            raise RuntimeError(f"Base table missing: {table_name}. Create the application schema before this migration.")
        return f"base table missing: {table_name} (dry-run only)"
    if column_name in existing:
        return f"{table_name}.{column_name} already exists"
    if context.execute:
        context.db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} VARCHAR(50)"))
        context.db.session.commit()
        return f"added {table_name}.{column_name}"
    return f"would add {table_name}.{column_name}"


def run_migration(context):
    actions = [
        _ensure_column(context, "properties", "electricity_policy_code"),
        _ensure_column(context, "properties", "water_policy_code"),
        _ensure_column(context, "rooms", "electricity_policy_code"),
        _ensure_column(context, "rooms", "water_policy_code"),
    ]
    summary = "; ".join(actions)
    if context.execute:
        return {"summary": f"Utility policy columns applied: {summary}"}
    return {"summary": f"Dry-run utility policy columns: {summary}"}
