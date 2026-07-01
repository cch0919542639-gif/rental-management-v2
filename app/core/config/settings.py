import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parents[3]


def _database_url() -> str:
    return os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'runtime.db'}")


def _is_postgresql_uri(uri: str) -> bool:
    return urlparse(uri).scheme.split("+", 1)[0] in {"postgresql", "postgres"}


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    JSON_AS_ASCII = False
    LINE_WEBHOOK_AUDIT_LOG = os.getenv("LINE_WEBHOOK_AUDIT_LOG", str(BASE_DIR / "logs" / "line_webhook_events.jsonl"))

    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
    OCR_API_KEY = os.getenv("OCR_API_KEY")
    OCR_PROVIDER = os.getenv("OCR_PROVIDER")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"


class PostgreSQLConfig(ProductionConfig):
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
        "pool_pre_ping": True,
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
    }


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "postgresql": PostgreSQLConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: str | None):
    config_key = (config_name or "default").lower()
    if config_key == "production" and _is_postgresql_uri(_database_url()):
        return PostgreSQLConfig
    return CONFIG_MAP.get(config_key, DevelopmentConfig)
