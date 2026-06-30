from flask import jsonify, render_template, request

from app.core.errors.exceptions import AppError


def _wants_json() -> bool:
    return request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json"


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        if _wants_json():
            payload = {"error": error.code, "message": error.message}
            if getattr(error, "details", None):
                payload["details"] = error.details
            return jsonify(payload), error.status_code
        return (
            render_template(
                "errors/app_error.html",
                error_code=error.code,
                title="操作失敗",
                message=error.message,
            ),
            error.status_code,
        )

    @app.errorhandler(404)
    def handle_not_found(_error):
        if _wants_json():
            return jsonify({"error": "not_found", "message": "Resource not found"}), 404
        return (
            render_template(
                "errors/404.html",
                title="找不到頁面",
                message="你要找的頁面不存在，或路徑已調整。",
            ),
            404,
        )

    @app.errorhandler(500)
    def handle_server_error(_error):
        if _wants_json():
            return jsonify({"error": "server_error", "message": "Internal server error"}), 500
        return (
            render_template(
                "errors/500.html",
                title="伺服器錯誤",
                message="系統發生未預期錯誤，請稍後再試或回報 Codex。",
            ),
            500,
        )
