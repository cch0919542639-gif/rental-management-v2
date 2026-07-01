from __future__ import annotations

from urllib.parse import urlparse


DEFAULT_SECRET = "change-me-in-production"


def validate_runtime_config(app):
    issues = get_runtime_config_issues(app)
    blocking = [issue for issue in issues if issue["severity"] == "error"]
    if blocking:
        details = "; ".join(issue["message"] for issue in blocking)
        raise RuntimeError(f"Invalid production configuration: {details}")

    for issue in issues:
        if issue["severity"] == "warning":
            app.logger.warning("Config warning: %s", issue["message"])


def get_runtime_config_issues(app) -> list[dict]:
    issues = []
    is_production = not app.debug and not app.testing
    secret_key = app.config.get("SECRET_KEY")
    database_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    parsed_db = urlparse(database_uri)

    if is_production and (not secret_key or secret_key == DEFAULT_SECRET):
        issues.append(
            {
                "severity": "error",
                "code": "secret_key",
                "message": "SECRET_KEY must be explicitly configured in production.",
            }
        )
    if is_production and not app.config.get("SESSION_COOKIE_SECURE"):
        issues.append(
            {
                "severity": "error",
                "code": "session_cookie_secure",
                "message": "SESSION_COOKIE_SECURE must be enabled in production.",
            }
        )
    if is_production and parsed_db.scheme == "sqlite":
        issues.append(
            {
                "severity": "warning",
                "code": "sqlite_production",
                "message": "SQLite is still in use; ensure backup/locking strategy is acceptable before launch.",
            }
        )
    if is_production and not app.config.get("PREFERRED_URL_SCHEME") == "https":
        issues.append(
            {
                "severity": "warning",
                "code": "preferred_url_scheme",
                "message": "PREFERRED_URL_SCHEME should be https in production.",
            }
        )
    return issues
