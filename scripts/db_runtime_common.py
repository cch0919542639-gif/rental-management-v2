from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_SQLITE_URL = "sqlite:///D:/CodexRuntime/rental/rebuild/runtime.db"
POSTGRES_DIALECTS = {"postgresql", "postgres"}


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)


def get_db_dialect(database_url: str) -> str:
    return urlparse(database_url).scheme.split("+", 1)[0]


def is_postgresql_url(database_url: str) -> bool:
    return get_db_dialect(database_url) in POSTGRES_DIALECTS


def resolve_sqlite_path(database_url: str) -> Path:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise SystemExit("This command only supports sqlite:/// DATABASE_URL values for SQLite mode.")
    return Path(database_url[len(prefix):])


def default_backup_suffix(database_url: str) -> str:
    return ".sql" if is_postgresql_url(database_url) else ".db"
