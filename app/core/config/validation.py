from __future__ import annotations

from urllib.parse import urlparse


DEFAULT_SECRET = "change-me-in-production"
POSTGRES_DIALECTS = {"postgresql", "postgres"}


def _detect_db_dialect(database_uri: str) -> str:
    return urlparse(database_uri).scheme.split("+", 1)[0]


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
    db_dialect = _detect_db_dialect(database_uri)

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
    if is_production and db_dialect == "sqlite":
        issues.append(
            {
                "severity": "error",
                "code": "sqlite_production",
                "message": "SQLite is not allowed for Phase 5 production. Configure a PostgreSQL DATABASE_URL.",
            }
        )
    if is_production and db_dialect and db_dialect not in POSTGRES_DIALECTS | {"sqlite"}:
        issues.append(
            {
                "severity": "warning",
                "code": "unsupported_phase5_dialect",
                "message": f"Database dialect '{db_dialect}' is unverified for the Phase 5 bridge; PostgreSQL is the supported target.",
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
