import logging


def configure_logging(app):
    level_name = "DEBUG" if app.debug or app.testing else "INFO"
    level = getattr(logging, level_name)
    app.logger.setLevel(level)

    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
        app.logger.addHandler(handler)
