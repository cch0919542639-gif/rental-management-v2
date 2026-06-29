from flask import Blueprint, jsonify

line_webhook_bp = Blueprint("line_webhook", __name__, url_prefix="/integrations/line")


@line_webhook_bp.post("/callback")
def line_callback():
    return (
        jsonify(
            {
                "error": "not_implemented",
                "message": "LINE webhook is reserved for Phase 3 implementation.",
            }
        ),
        501,
    )
