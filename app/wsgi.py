import os

from app import create_app


def create_wsgi_app():
    return create_app(os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development")


app = create_wsgi_app()
