from __future__ import annotations

import base64
import hashlib
import hmac
import json

from flask import Blueprint, current_app, jsonify, request

line_webhook_bp = Blueprint("line_webhook", __name__, url_prefix="/integrations/line")


def _compute_signature(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def _verify_signature(body: bytes, signature: str | None, secret: str) -> bool:
    if not signature:
        return False
    expected = _compute_signature(body, secret)
    return hmac.compare_digest(signature, expected)


def _summarize_event(event: dict) -> dict:
    source = event.get("source") or {}
    message = event.get("message") or {}
    return {
        "type": event.get("type"),
        "source_type": source.get("type"),
        "user_id": source.get("userId"),
        "message_type": message.get("type"),
        "message_id": message.get("id"),
        "reply_token_present": bool(event.get("replyToken")),
    }


@line_webhook_bp.post("/callback")
def line_callback():
    secret = current_app.config.get("LINE_CHANNEL_SECRET")
    if not secret:
        return (
            jsonify(
                {
                    "error": "not_configured",
                    "message": "LINE webhook secret is not configured.",
                }
            ),
            501,
        )

    body = request.get_data(cache=False)
    signature = request.headers.get("X-Line-Signature")
    if not _verify_signature(body, signature, secret):
        return (
            jsonify(
                {
                    "error": "invalid_signature",
                    "message": "LINE webhook signature verification failed.",
                }
            ),
            401,
        )

    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return (
            jsonify(
                {
                    "error": "invalid_payload",
                    "message": "LINE webhook payload must be valid JSON.",
                }
            ),
            400,
        )

    events = payload.get("events")
    if not isinstance(events, list):
        return (
            jsonify(
                {
                    "error": "invalid_payload",
                    "message": "LINE webhook payload must include an events array.",
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "status": "accepted",
                "event_count": len(events),
                "reply_capable": bool(current_app.config.get("LINE_CHANNEL_ACCESS_TOKEN")),
                "events": [_summarize_event(event) for event in events],
                "message": "LINE webhook accepted. Downstream processing remains manual-review only.",
            }
        ),
        200,
    )
