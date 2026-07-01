from datetime import date

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

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
    return jsonify({"ok": True, "checks": {"database": "skipped"}})
