from flask import abort

from app.core.db import db


def session_get_or_404(model, object_id):
    instance = db.session.get(model, object_id)
    if instance is None:
        abort(404)
    return instance
