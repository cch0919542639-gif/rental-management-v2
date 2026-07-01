"""
Phase 4 baseline marker migration.

Purpose:
  - Establish versioned migration tracking in the rebuild project
  - Record the baseline before future schema/data write migrations

Rollback:
  - Remove the corresponding row from schema_migration_log only if this
    marker was recorded by mistake.

Verification:
  - Run `py -3 .\scripts\migration\run_migrations.py --list`
  - Confirm this migration appears as applied after `--execute`
"""

MIGRATION_ID = "20260701_000001_phase4_baseline_marker"
DESCRIPTION = "Create the first tracked migration boundary for Phase 4. No schema/data changes."


def run_migration(context):
    if context.execute:
        return {"summary": "Baseline marker recorded. No application tables changed."}
    return {"summary": "Dry-run baseline marker. No application tables changed."}
