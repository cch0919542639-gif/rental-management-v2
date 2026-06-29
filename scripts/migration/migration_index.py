"""
migration_index.py

Read-only migration entrypoint index for Phase 2.

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
        "type": "read-only scan",
        "safety": "safe",
        "description": "Scan virtual tenant names and invalid room statuses for maintenance migration prep.",
    },
    "migration_index.py": {
        "type": "index",
        "safety": "safe",
        "description": "List available migration scripts and usage notes.",
    },
}


def main():
    print("=" * 72)
    print("Migration Script Index")
    print("=" * 72)
    for script_path in sorted(ROOT.glob("*.py")):
        if script_path.name.startswith("_"):
            continue
        note = SCRIPT_NOTES.get(
            script_path.name,
            {
                "type": "unknown",
                "safety": "review-required",
                "description": "No index note yet. Review file manually before use.",
            },
        )
        print(f"Script      : {script_path.name}")
        print(f"Type        : {note['type']}")
        print(f"Safety      : {note['safety']}")
        print(f"Description : {note['description']}")
        print(f"Path        : {script_path}")
        print("-" * 72)

    print("Rule: do not run write-capable migration scripts without Codex review.")
    print("=" * 72)


if __name__ == "__main__":
    main()
