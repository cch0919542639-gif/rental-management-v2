"""
migration_index.py

Read-only migration entrypoint index for Phase 3.

Purpose:
  - List currently available migration scripts
  - Show safety level and execution notes
  - Give operators a single discovery entrypoint

This script does NOT modify the database.

Usage:
    cd D:\\CodexRuntime\\rental\\rebuild
    py -3 .\\scripts\\migration\\migration_index.py
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parent

SCRIPT_NOTES = {
    "apply_20260701_000001_phase4_baseline_marker.py": {
        "mode": "apply",
        "type": "baseline marker",
        "safety": "safe",
        "requires_review": "yes",
        "verification": "Run run_migrations.py --list and confirm the marker status changes after --execute.",
        "rollback": "Delete the schema_migration_log row only if this marker was recorded by mistake.",
        "description": "Record the first tracked migration boundary for Phase 4 without changing domain tables.",
    },
    "apply_20260701_000002_alembic_bridge.py": {
        "mode": "apply",
        "type": "bridge marker",
        "safety": "review-required",
        "requires_review": "yes",
        "verification": "Dry-run first, then verify alembic_version and schema_migration_log stay in sync after execute.",
        "rollback": "Delete the alembic_version row/table and remove the bridge entry from schema_migration_log if execution must be reverted.",
        "description": "Final custom-runner migration that stamps the Alembic baseline revision before Phase 5 cutover.",
    },
    "maintenance_legacy_scan.py": {
        "mode": "scan",
        "type": "read-only scan",
        "safety": "safe",
        "requires_review": "no",
        "verification": "Review printed candidate rows and room status anomalies.",
        "rollback": "No rollback needed; script is read-only.",
        "description": "Scan virtual tenant names and invalid room statuses for maintenance migration prep.",
    },
    "export_sqlite_to_pg.py": {
        "mode": "export",
        "type": "drill scaffold",
        "safety": "safe",
        "requires_review": "no",
        "verification": "Run dry-run first, then confirm manifest.json and CSV counts after --execute.",
        "rollback": "Delete generated export directory only; source DB is read-only.",
        "description": "Preview or export SQLite rows in FK-safe order for PostgreSQL migration drills.",
    },
    "verify_row_parity.py": {
        "mode": "verify",
        "type": "read-only parity check",
        "safety": "safe",
        "requires_review": "no",
        "verification": "Compare identical databases first, then compare source vs imported target before cutover.",
        "rollback": "No rollback needed; script is read-only.",
        "description": "Compare per-table row counts between source and target databases.",
    },
    "migration_index.py": {
        "mode": "index",
        "type": "index",
        "safety": "safe",
        "requires_review": "no",
        "verification": "Confirm listed scripts and safety notes match repository contents.",
        "rollback": "No rollback needed; script is read-only.",
        "description": "List available migration scripts and usage notes.",
    },
    "run_migrations.py": {
        "mode": "runner",
        "type": "migration runner",
        "safety": "review-required",
        "requires_review": "yes",
        "verification": "Use --list first, then run with --execute only after reviewing pending migration details.",
        "rollback": "Depends on each migration; review the target migration file before execution.",
        "description": "List, dry-run, or execute versioned apply_* migrations and record applied IDs.",
    },
    "_template_write_migration.py": {
        "mode": "template",
        "type": "write scaffold",
        "safety": "review-required",
        "requires_review": "yes",
        "verification": "Copy into a real migration and replace placeholder checks before use.",
        "rollback": "Define an exact rollback note in the derived migration before --execute.",
        "description": "Reference scaffold for future write-capable migration scripts.",
    },
}


def main():
    print("=" * 72)
    print("Migration Script Index")
    print("=" * 72)
    for script_path in sorted(ROOT.glob("*.py")):
        if script_path.name.startswith("_") and script_path.name != "_template_write_migration.py":
            continue
        note = SCRIPT_NOTES.get(
            script_path.name,
            {
                "mode": "unknown",
                "type": "unknown",
                "safety": "review-required",
                "requires_review": "yes",
                "verification": "Review file manually before use.",
                "rollback": "Review file manually before any write execution.",
                "description": "No index note yet. Review file manually before use.",
            },
        )
        print(f"Script      : {script_path.name}")
        print(f"Mode        : {note['mode']}")
        print(f"Type        : {note['type']}")
        print(f"Safety      : {note['safety']}")
        print(f"Review      : {note['requires_review']}")
        print(f"Description : {note['description']}")
        print(f"Verify      : {note['verification']}")
        print(f"Rollback    : {note['rollback']}")
        print(f"Path        : {script_path}")
        print("-" * 72)

    print("Rule: do not run write-capable migration scripts without Codex review.")
    print("Naming: scan_* = read-only, plan_* = planning only, apply_* = write-capable with --execute.")
    print("Runner: use run_migrations.py --list before any --execute.")
    print("Bridge: do not execute the Alembic bridge until the Phase 5B gate is explicitly approved.")
    print("=" * 72)


if __name__ == "__main__":
    main()
