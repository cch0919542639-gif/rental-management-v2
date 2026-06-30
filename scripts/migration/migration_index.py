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
    "maintenance_legacy_scan.py": {
        "mode": "scan",
        "type": "read-only scan",
        "safety": "safe",
        "requires_review": "no",
        "verification": "Review printed candidate rows and room status anomalies.",
        "rollback": "No rollback needed; script is read-only.",
        "description": "Scan virtual tenant names and invalid room statuses for maintenance migration prep.",
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
    print("=" * 72)


if __name__ == "__main__":
    main()
