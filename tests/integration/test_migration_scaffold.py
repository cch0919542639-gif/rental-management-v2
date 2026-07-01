from pathlib import Path
import os
import subprocess
import sys


def _run_script(script_path: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
        cwd=script_path.parents[2],
        check=True,
    )


def test_migration_index_lists_scaffold_metadata():
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "migration" / "migration_index.py"
    result = _run_script(script)
    assert "Migration Script Index" in result.stdout
    assert "_template_write_migration.py" in result.stdout
    assert "Mode        : template" in result.stdout
    assert "Naming: scan_* = read-only, plan_* = planning only, apply_* = write-capable with --execute." in result.stdout


def test_migration_template_runs_in_dry_run_mode():
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "migration" / "_template_write_migration.py"
    result = _run_script(script, "--reference-date", "2026-06-30")
    assert "Template Write Migration (DRY-RUN)" in result.stdout
    assert "Reference date : 2026-06-30" in result.stdout
    assert "Dry-run scaffold only. No database changes." in result.stdout


def test_phase5_bridge_and_baseline_scaffold_exist():
    root = Path(__file__).resolve().parents[2]
    baseline = root / "app" / "migrations" / "versions" / "20260701_000001_phase5_baseline.py"
    bridge = root / "scripts" / "migration" / "apply_20260701_000002_alembic_bridge.py"

    assert baseline.exists()
    assert bridge.exists()
    assert 'revision = "20260701_000001"' in baseline.read_text(encoding="utf-8")


def test_phase5_bridge_runs_in_dry_run_mode():
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "migration" / "run_migrations.py"
    result = _run_script(script, "--id", "20260701_000002_alembic_bridge")
    assert "Dry-run only." in result.stdout
    assert "alembic_version" in result.stdout


def test_phase5_bridge_execute_requires_explicit_gate(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "migration" / "run_migrations.py"
    db_path = tmp_path / "bridge-gated.db"
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"
    env["SCRIPT_APP_CONFIG"] = "default"
    env["SECRET_KEY"] = "test-secret"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--execute",
            "--id",
            "20260701_000002_alembic_bridge",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
    )

    assert result.returncode == 1
    assert "--allow-bridge" in result.stderr or "--allow-bridge" in result.stdout


def test_phase5_bridge_execute_requires_prior_migrations(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "migration" / "run_migrations.py"
    db_path = tmp_path / "bridge-prior.db"
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"
    env["SCRIPT_APP_CONFIG"] = "default"
    env["SECRET_KEY"] = "test-secret"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--execute",
            "--allow-bridge",
            "--id",
            "20260701_000002_alembic_bridge",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
    )

    assert result.returncode == 1
    assert "Pending before bridge" in result.stderr or "Pending before bridge" in result.stdout


def test_phase5_bridge_execute_stamps_revision_after_prior_migrations(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "migration" / "run_migrations.py"
    db_path = tmp_path / "bridge-success.db"
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"
    env["SCRIPT_APP_CONFIG"] = "default"
    env["SECRET_KEY"] = "test-secret"

    baseline = subprocess.run(
        [
            sys.executable,
            str(script),
            "--execute",
            "--id",
            "20260701_000001_phase4_baseline_marker",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert "Applied and recorded." in baseline.stdout

    bridge = subprocess.run(
        [
            sys.executable,
            str(script),
            "--execute",
            "--allow-bridge",
            "--id",
            "20260701_000002_alembic_bridge",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        check=True,
    )
    assert "Alembic stamped at revision 20260701_000001" in bridge.stdout
    assert "Applied and recorded." in bridge.stdout
