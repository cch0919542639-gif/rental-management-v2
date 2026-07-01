from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

try:
    from flask_migrate import Migrate
except ImportError:  # pragma: no cover - local env may not have phase5 deps yet
    class Migrate:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            pass

        def init_app(self, app, db):
            app.extensions.setdefault("migrate_unavailable", True)

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate(compare_type=True)


def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "請先登入"
