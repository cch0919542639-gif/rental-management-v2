from pathlib import Path
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
