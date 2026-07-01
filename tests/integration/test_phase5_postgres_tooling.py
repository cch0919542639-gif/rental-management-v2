from pathlib import Path
import os
import subprocess
import sys


def _run_script(script_path: Path, *args: str, env: dict | None = None):
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
        cwd=script_path.parents[1],
        env=env,
    )


def test_check_postgres_tooling_rejects_sqlite_database_url(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "check_postgres_tooling.py"
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///runtime.db"
    env["SECRET_KEY"] = "phase5-secret"

    result = _run_script(script, env=env)

    assert result.returncode == 1
    assert "must be PostgreSQL" in result.stdout


def test_check_postgres_tooling_passes_with_fake_binaries(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "check_postgres_tooling.py"
    fake_bin_dir = tmp_path / "bin"
    fake_bin_dir.mkdir()
    fake_pg_dump = fake_bin_dir / "fake_pg_dump.cmd"
    fake_psql = fake_bin_dir / "fake_psql.cmd"
    fake_pg_dump.write_text("@echo off\r\necho fake pg_dump\r\n", encoding="utf-8")
    fake_psql.write_text("@echo off\r\necho fake psql\r\n", encoding="utf-8")

    env = os.environ.copy()
    env["DATABASE_URL"] = "postgresql://postgres:secret@127.0.0.1:5432/rental_rebuild"
    env["SECRET_KEY"] = "phase5-secret"
    env["PATH"] = f"{fake_bin_dir}{os.pathsep}{env['PATH']}"

    result = _run_script(
        script,
        "--pg-dump-bin",
        "fake_pg_dump",
        "--psql-bin",
        "fake_psql",
        env=env,
    )

    assert result.returncode == 0
    assert "PostgreSQL preflight passed." in result.stdout


def test_check_postgres_tooling_can_skip_binary_checks(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "check_postgres_tooling.py"
    env = os.environ.copy()
    env["DATABASE_URL"] = "postgresql://postgres:secret@127.0.0.1:5432/rental_rebuild"
    env["SECRET_KEY"] = "phase5-secret"

    result = _run_script(script, "--skip-binaries", env=env)

    assert result.returncode == 0
    assert "Binary checks skipped" in result.stdout
