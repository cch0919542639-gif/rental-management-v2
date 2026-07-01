from datetime import date

from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import login_required
from sqlalchemy import text

from app.core.config import get_runtime_config_issues
from app.services import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
@login_required
def dashboard_home():
    year_month = request.args.get("month", date.today().strftime("%Y-%m"))
    summary = DashboardService.get_summary(year_month)
    return render_template("dashboard/index.html", **summary)


@dashboard_bp.get("/healthz")
def healthz():
    return {"ok": True}


@dashboard_bp.get("/readyz")
def readyz():
    issues = get_runtime_config_issues(current_app)
    checks = {"database": "ok", "config": "ok"}

    if current_app.testing:
        checks["database"] = "skipped"
    else:
        from app.core.db import db

        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            checks["database"] = "error"

    if issues:
        checks["config"] = "warning"

    ok = checks["database"] != "error"
    status_code = 200 if ok else 503
    return jsonify({"ok": ok, "checks": checks, "issues": issues}), status_code
