from flask import jsonify, request

from app.core.errors.exceptions import AppError


def _wants_json() -> bool:
    return request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json"


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        if _wants_json():
            return jsonify({"error": error.code, "message": error.message}), error.status_code
        return error.message, error.status_code

    @app.errorhandler(404)
    def handle_not_found(_error):
        if _wants_json():
            return jsonify({"error": "not_found", "message": "Resource not found"}), 404
        return "Not Found", 404

    @app.errorhandler(500)
    def handle_server_error(_error):
        if _wants_json():
            return jsonify({"error": "server_error", "message": "Internal server error"}), 500
        return "Internal Server Error", 500
