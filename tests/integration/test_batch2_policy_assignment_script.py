import sqlite3
import subprocess
import sys
from pathlib import Path


def _create_target(path: Path, *, conflict: bool = False):
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE properties ("
            "id INTEGER PRIMARY KEY, name TEXT NOT NULL, "
            "electricity_policy_code TEXT, water_policy_code TEXT)"
        )
        for property_id in (1, 2, 3, 4, 5, 6, 21, 22):
            electricity = "electricity_fixed_rate" if conflict and property_id == 1 else None
            conn.execute(
                "INSERT INTO properties (id, name, electricity_policy_code, water_policy_code) VALUES (?, ?, ?, ?)",
                (property_id, f"Property {property_id}", electricity, None),
            )


def _run_script(root: Path, database_url: str, *args: str):
    return subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "real_import" / "apply_batch2_utility_policies.py"),
            "--database-url",
            database_url,
            *args,
        ],
        capture_output=True,
        text=True,
        cwd=root,
    )


def test_batch2_policy_assignment_dry_run_then_execute(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "batch2-target.db"
    _create_target(db_path)
    database_url = f"sqlite:///{db_path}"

    dry_run = _run_script(root, database_url)
    assert dry_run.returncode == 0
    assert "Candidate count: 8" in dry_run.stdout

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT electricity_policy_code FROM properties WHERE id = 5").fetchone()[0] is None

    execute = _run_script(root, database_url, "--execute")
    assert execute.returncode == 0
    assert "Configured count: 8" in execute.stdout

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT electricity_policy_code FROM properties WHERE id = 5").fetchone()[0] == (
            "electricity_bill_usage_ratio_plus_public_share"
        )
        assert conn.execute("SELECT water_policy_code FROM properties WHERE id = 22").fetchone()[0] == (
            "water_bill_by_stay_days"
        )


def test_batch2_policy_assignment_rejects_conflicting_existing_value(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db_path = tmp_path / "batch2-conflict.db"
    _create_target(db_path, conflict=True)

    result = _run_script(root, f"sqlite:///{db_path}", "--execute")

    assert result.returncode == 1
    assert "STOP: Existing policy values conflict" in result.stdout
