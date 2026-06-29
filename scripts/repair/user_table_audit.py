"""
user_table_audit.py

Read-only audit for `user` / `users` dual-table scenario.

Checks:
  - whether table `users` exists
  - row count in `user`
  - row count in `users` when present

Usage:
    cd D:\\CodexRuntime\\rental\\rebuild
    py -3 .\\scripts\\repair\\user_table_audit.py
"""

from pathlib import Path
import sys

from sqlalchemy import inspect, text

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.repair._common import build_script_app
from app.core.db import db


def _count(table_name: str) -> int:
    return db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()


def main():
    app = build_script_app()
    with app.app_context():
        inspector = inspect(db.engine)
        table_names = set(inspector.get_table_names())
        has_user = "user" in table_names
        has_users = "users" in table_names

        print("=" * 72)
        print("User Table Audit (read-only)")
        print("=" * 72)
        print(f"Has table `user` : {has_user}")
        print(f"Has table `users`: {has_users}")
        if has_user:
            print(f"`user` row count : {_count('user')}")
        if has_users:
            print(f"`users` row count: {_count('users')}")
        print("=" * 72)


if __name__ == "__main__":
    main()
