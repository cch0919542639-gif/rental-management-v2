from pathlib import Path
import os
import sqlite3
import subprocess
import sys


def test_backup_runtime_db_creates_timestamped_copy(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "runtime.db"
    db_path.write_bytes(b"phase4-backup-test")
    backup_dir = tmp_path / "backups"

    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "backup_runtime_db.py"),
            "--output-dir",
            str(backup_dir),
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )

    backups = list(backup_dir.glob("runtime_*.db"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == b"phase4-backup-test"
    assert "SQLite Backup Complete" in result.stdout


def test_restore_runtime_db_requires_execute_and_can_restore(tmp_path):
    root = Path(__file__).resolve().parents[2]
    target_db = tmp_path / "runtime.db"
    source_backup = tmp_path / "restore-source.db"

    target_db.write_bytes(b"old-db")
    source_backup.write_bytes(b"restored-db")

    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{target_db}"

    dry_run = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "restore_runtime_db.py"),
            "--source",
            str(source_backup),
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert "Dry-run only" in dry_run.stdout
    assert target_db.read_bytes() == b"old-db"

    execute = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "restore_runtime_db.py"),
            "--source",
            str(source_backup),
            "--execute",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert "Restore complete." in execute.stdout
    assert target_db.read_bytes() == b"restored-db"
