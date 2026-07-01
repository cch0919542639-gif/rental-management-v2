"""
_template_write_migration.py

Template for future write-capable migration scripts.

Purpose:
  - Show the required dry-run-first structure
  - Standardize CLI flags and operator guidance
  - Prevent ad-hoc write migrations without verification notes

This file is a scaffold only. Do not run it as a real migration.
"""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.migration._common import build_script_app, is_execute_mode, parse_reference_date

MIGRATION_ID = "YYYYMMDD_HHMMSS_short_name"
DESCRIPTION = "Replace with a precise one-line migration description."


def _build_parser():
    parser = argparse.ArgumentParser(description="Template scaffold for write-capable migrations")
    parser.add_argument("--execute", action="store_true", help="Apply the migration instead of dry-run")
    parser.add_argument("--reference-date", help="Optional ISO date used by date-sensitive migrations")
    return parser


def main(argv: list[str]):
    args = _build_parser().parse_args(argv)
    execute = is_execute_mode(args.execute)
    reference_date = parse_reference_date(args.reference_date)
    app = build_script_app()

    with app.app_context():
        print("=" * 72)
        print(f"Template Write Migration ({'EXECUTE' if execute else 'DRY-RUN'})")
        print("=" * 72)
        print(f"Migration ID   : {MIGRATION_ID}")
        print(f"Description    : {DESCRIPTION}")
        print("Purpose        : Replace this file with a real migration implementation.")
        print(f"Reference date : {reference_date.isoformat()}")
        print("Verification   : Document pre-check, post-check, and affected row summary.")
        print("Rollback note  : Document exact rollback path before enabling --execute.")
        print("-" * 72)
        if execute:
            print("Template only. Do not execute without replacing scaffold logic.")
        else:
            print("Dry-run scaffold only. No database changes.")
        print("=" * 72)


def run_migration(context):
    return {
        "summary": "Template only. Replace this scaffold with real migration logic before use.",
    }


if __name__ == "__main__":
    main(sys.argv[1:])
