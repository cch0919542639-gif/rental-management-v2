from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.db_runtime_common import get_database_url, get_db_dialect, is_postgresql_url, resolve_sqlite_path


def _build_parser():
    parser = argparse.ArgumentParser(description="Restore the configured runtime database from a backup file.")
    parser.add_argument("--source", required=True, help="Path to a backup file")
    parser.add_argument("--execute", action="store_true", help="Actually overwrite the configured database")
    parser.add_argument("--psql-bin", default="psql", help="psql executable for PostgreSQL restore")
    return parser


def main():
    args = _build_parser().parse_args()
    source = Path(args.source)
    database_url = get_database_url()
    driver = get_db_dialect(database_url)

    if not source.exists():
        raise SystemExit(f"Backup source not found: {source}")

    if is_postgresql_url(database_url):
        command = [
            args.psql_bin,
            "--dbname",
            database_url,
            "--file",
            str(source),
        ]
        print("=" * 72)
        print(f"Driver       : {driver}")
        print(f"Restore Mode : {'EXECUTE' if args.execute else 'DRY-RUN'}")
        print(f"Source       : {source}")
        print(f"Command      : {' '.join(command)}")
        print("=" * 72)
        if not args.execute:
            print("Dry-run only. Re-run with --execute to restore the PostgreSQL database.")
            return

        subprocess.run(command, check=True)
        print("Restore complete.")
        return

    target = resolve_sqlite_path(database_url)
    print("=" * 72)
    print(f"Driver       : {driver}")
    print(f"Restore Mode : {'EXECUTE' if args.execute else 'DRY-RUN'}")
    print(f"Source       : {source}")
    print(f"Target       : {target}")
    print("=" * 72)

    if not args.execute:
        print("Dry-run only. Re-run with --execute to overwrite the target database.")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    print("Restore complete.")


if __name__ == "__main__":
    main()
