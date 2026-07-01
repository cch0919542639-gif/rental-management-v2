from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.db_runtime_common import (
    default_backup_suffix,
    get_database_url,
    get_db_dialect,
    is_postgresql_url,
    resolve_sqlite_path,
)


def _build_parser():
    parser = argparse.ArgumentParser(description="Create a timestamped backup for the configured runtime database.")
    parser.add_argument(
        "--output-dir",
        default="backups",
        help="Directory where backup files are written (default: backups)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the backup plan without executing it")
    parser.add_argument("--pg-dump-bin", default="pg_dump", help="pg_dump executable for PostgreSQL backups")
    return parser


def main():
    args = _build_parser().parse_args()
    database_url = get_database_url()
    driver = get_db_dialect(database_url)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = output_dir / f"runtime_{timestamp}{default_backup_suffix(database_url)}"

    print("=" * 72)
    print(f"Driver : {driver}")
    print(f"Mode   : {'DRY-RUN' if args.dry_run else 'EXECUTE'}")

    if is_postgresql_url(database_url):
        command = [
            args.pg_dump_bin,
            "--dbname",
            database_url,
            "--file",
            str(target),
            "--format",
            "plain",
        ]
        print(f"Backup : {target}")
        print(f"Command: {' '.join(command)}")
        print("=" * 72)
        if args.dry_run:
            print("Dry-run only. Re-run without --dry-run to execute pg_dump.")
            return

        subprocess.run(command, check=True)
        print("PostgreSQL Backup Complete")
        print("=" * 72)
        return

    source = resolve_sqlite_path(database_url)
    if not source.exists():
        raise SystemExit(f"Database file not found: {source}")

    print("=" * 72)
    print(f"Source : {source}")
    print(f"Backup : {target}")
    print("=" * 72)
    if args.dry_run:
        print("Dry-run only. Re-run without --dry-run to copy the SQLite database.")
        return

    shutil.copy2(source, target)
    print("SQLite Backup Complete")
    print("=" * 72)


if __name__ == "__main__":
    main()
