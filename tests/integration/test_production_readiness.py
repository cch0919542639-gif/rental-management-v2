from flask import Flask

from app.core.config import get_runtime_config_issues, validate_runtime_config


def test_validate_runtime_config_rejects_default_secret_in_production():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="change-me-in-production",
        SQLALCHEMY_DATABASE_URI="postgresql://example",
        SESSION_COOKIE_SECURE=True,
        PREFERRED_URL_SCHEME="https",
        DEBUG=False,
        TESTING=False,
    )
    try:
        validate_runtime_config(app)
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert "SECRET_KEY" in str(exc)


def test_get_runtime_config_issues_warns_for_sqlite_in_production():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="safe-secret",
        SQLALCHEMY_DATABASE_URI="sqlite:///runtime.db",
        SESSION_COOKIE_SECURE=True,
        PREFERRED_URL_SCHEME="https",
        DEBUG=False,
        TESTING=False,
    )
    issues = get_runtime_config_issues(app)
    assert any(item["code"] == "sqlite_production" for item in issues)


def test_readyz_returns_ok_for_testing_app(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["checks"]["database"] == "skipped"
