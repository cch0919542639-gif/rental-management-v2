r"""Create one local administrator account through an interactive terminal prompt.

The password is read with ``getpass`` and is never echoed, printed, or placed
in a command-line argument. Use this only for a controlled local environment.

Example:
    py -3 .\scripts\create_local_admin.py --database-url sqlite:///D:\CodexRuntime\rental\rebuild\runtime-real.db
"""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _build_parser():
    parser = argparse.ArgumentParser(description="Create a local rental-system administrator")
    parser.add_argument("--database-url", required=True, help="Explicit target database URL")
    parser.add_argument("--username", help="Login username; prompts when omitted")
    parser.add_argument("--name", help="Display name; prompts when omitted")
    return parser


def main(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    os.environ["DATABASE_URL"] = args.database_url
    os.environ.setdefault("SCRIPT_APP_CONFIG", "default")
    os.environ.setdefault("SECRET_KEY", "local-admin-bootstrap")

    # Import after DATABASE_URL is configured because settings are evaluated
    # during application import.
    from app import create_app
    from app.core.db import db
    from app.models import User

    username = (args.username or input("Username: ")).strip()
    name = (args.name or input("Display name: ")).strip()
    if not username or not name:
        raise SystemExit("Username and display name are required.")

    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if not password:
        raise SystemExit("Password is required.")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    app = create_app("default")
    with app.app_context():
        if User.query.filter_by(username=username).first() is not None:
            raise SystemExit(f"Username already exists: {username}")
        user = User(username=username, name=name, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    print(f"Created local administrator: {username}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
