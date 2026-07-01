from flask import Flask

from app.core.config import get_config, validate_runtime_config
from app.core.db import init_extensions
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.core.year_month import to_ui_year_month
from app.modules import register_blueprints


def create_app(config_name: str | None = None) -> Flask:
    flask_app = Flask(__name__, template_folder="../../templates", static_folder="../../static")
    flask_app.config.from_object(get_config(config_name))

    init_extensions(flask_app)
    configure_logging(flask_app)
    validate_runtime_config(flask_app)
    register_error_handlers(flask_app)
    register_blueprints(flask_app)

    flask_app.add_template_filter(to_ui_year_month, "year_month_ui")

    # Import models after extensions so SQLAlchemy metadata is populated.
    import app.models  # noqa: F401

    return flask_app
