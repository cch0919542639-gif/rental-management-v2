"""
Final custom-runner migration before Alembic becomes authoritative.

Purpose:
  - Discover the current Alembic head revision from app/migrations/versions/
  - Create Alembic's alembic_version table if missing
  - Stamp the discovered head revision into alembic_version
  - Prepare the repository for the custom-runner -> Alembic cutover

Rollback:
  - Delete the row from alembic_version
  - Drop alembic_version if it was created only for this bridge
  - Delete this migration's row from schema_migration_log if the runner recorded it

Verification:
  - py -3 .\scripts\migration\run_migrations.py --list
  - Confirm this bridge migration appears as pending before execute
  - After execute: SELECT * FROM alembic_version
  - After execute: flask db current (once Flask-Migrate is installed)
"""

from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import text

MIGRATION_ID = "20260701_000002_alembic_bridge"
DESCRIPTION = "Stamp the Alembic baseline revision. Final custom-runner bridge."

ALEMBIC_VERSION_TABLE = "alembic_version"
REVISION_RE = re.compile(r"^revision\s*=\s*[\"']([^\"']+)[\"']")


def _versions_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "app" / "migrations" / "versions"


def _find_head_revision() -> str:
    candidates = [path for path in sorted(_versions_dir().glob("*.py")) if path.name != "__init__.py"]
    if not candidates:
        raise RuntimeError("No Alembic revision files found. Create a baseline revision before the bridge.")

    latest = candidates[-1]
    for line in latest.read_text(encoding="utf-8").splitlines():
        match = REVISION_RE.match(line.strip())
        if match:
            return match.group(1)
    raise RuntimeError(f"Could not parse revision id from {latest.name}")


def _stamp_revision(context, revision_id: str):
    bind = context.db.session
    bind.execute(
        text(
            f"""
            CREATE TABLE IF NOT EXISTS {ALEMBIC_VERSION_TABLE} (
                version_num VARCHAR(32) PRIMARY KEY
            )
            """
        )
    )
    bind.execute(text(f"DELETE FROM {ALEMBIC_VERSION_TABLE}"))
    bind.execute(
        text(f"INSERT INTO {ALEMBIC_VERSION_TABLE} (version_num) VALUES (:revision_id)"),
        {"revision_id": revision_id},
    )
    bind.commit()


def run_migration(context):
    revision_id = _find_head_revision()
    if not context.execute:
        return {
            "summary": (
                f"Dry-run only. Would stamp Alembic head revision {revision_id} "
                f"into {ALEMBIC_VERSION_TABLE}."
            )
        }

    _stamp_revision(context, revision_id)
    return {
        "summary": (
            f"Alembic stamped at revision {revision_id}. "
            "Use flask db current / flask db upgrade for post-bridge verification."
        )
    }
