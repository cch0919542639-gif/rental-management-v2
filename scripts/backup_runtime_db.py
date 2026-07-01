from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import shutil


def _build_parser():
    parser = argparse.ArgumentParser(description="Create a timestamped backup for the configured SQLite database.")
    parser.add_argument(
        "--output-dir",
        default="backups",
        help="Directory where backup files are written (default: backups)",
    )
    return parser


def _resolve_sqlite_path() -> Path:
    database_url = os.getenv("DATABASE_URL", "sqlite:///D:/CodexRuntime/rental/rebuild/runtime.db")
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise SystemExit("backup_runtime_db.py only supports sqlite:/// DATABASE_URL values.")
    return Path(database_url[len(prefix):])


def main():
    args = _build_parser().parse_args()
    source = _resolve_sqlite_path()
    if not source.exists():
        raise SystemExit(f"Database file not found: {source}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = output_dir / f"{source.stem}_{timestamp}{source.suffix}"
    shutil.copy2(source, target)

    print("=" * 72)
    print("SQLite Backup Complete")
    print("=" * 72)
    print(f"Source : {source}")
    print(f"Backup : {target}")
    print("=" * 72)


if __name__ == "__main__":
    main()
