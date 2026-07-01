from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil


def _build_parser():
    parser = argparse.ArgumentParser(description="Restore the configured SQLite database from a backup file.")
    parser.add_argument("--source", required=True, help="Path to a backup sqlite file")
    parser.add_argument("--execute", action="store_true", help="Actually overwrite the configured database")
    return parser


def _resolve_sqlite_path() -> Path:
    database_url = os.getenv("DATABASE_URL", "sqlite:///D:/CodexRuntime/rental/rebuild/runtime.db")
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise SystemExit("restore_runtime_db.py only supports sqlite:/// DATABASE_URL values.")
    return Path(database_url[len(prefix):])


def main():
    args = _build_parser().parse_args()
    source = Path(args.source)
    target = _resolve_sqlite_path()

    if not source.exists():
        raise SystemExit(f"Backup source not found: {source}")

    print("=" * 72)
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
