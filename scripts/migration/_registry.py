from __future__ import annotations

from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from sqlalchemy import text


MIGRATION_LOG_TABLE = "schema_migration_log"


@dataclass(frozen=True)
class MigrationDefinition:
    migration_id: str
    description: str
    path: Path
    module: object


@dataclass
class MigrationContext:
    app: object
    db: object
    execute: bool


def ensure_migration_log_table(db):
    db.session.execute(
        text(
            f"""
            CREATE TABLE IF NOT EXISTS {MIGRATION_LOG_TABLE} (
                migration_id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )
    db.session.commit()


def get_applied_migration_ids(db) -> set[str]:
    ensure_migration_log_table(db)
    rows = db.session.execute(text(f"SELECT migration_id FROM {MIGRATION_LOG_TABLE}")).all()
    return {row[0] for row in rows}


def record_migration(db, migration: MigrationDefinition):
    db.session.execute(
        text(
            f"""
            INSERT INTO {MIGRATION_LOG_TABLE} (migration_id, description)
            VALUES (:migration_id, :description)
            """
        ),
        {"migration_id": migration.migration_id, "description": migration.description},
    )
    db.session.commit()


def discover_migrations(root: Path) -> list[MigrationDefinition]:
    migrations: list[MigrationDefinition] = []
    for path in sorted(root.glob("apply_*.py")):
        spec = spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load migration module: {path.name}")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        migration_id = getattr(module, "MIGRATION_ID", path.stem)
        description = getattr(module, "DESCRIPTION", "No description provided.")
        run_migration = getattr(module, "run_migration", None)
        if not callable(run_migration):
            raise RuntimeError(f"Migration {path.name} must define run_migration(context)")
        migrations.append(
            MigrationDefinition(
                migration_id=migration_id,
                description=description,
                path=path,
                module=module,
            )
        )
    return migrations
