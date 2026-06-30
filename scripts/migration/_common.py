from __future__ import annotations

from datetime import date
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app


def build_script_app():
    config_name = os.getenv("SCRIPT_APP_CONFIG", "default")
    return create_app(config_name)


def parse_reference_date(raw: str | None) -> date:
    if not raw:
        return date.today()
    return date.fromisoformat(raw)


def is_execute_mode(flag: bool) -> bool:
    return bool(flag)
