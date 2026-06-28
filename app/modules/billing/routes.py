from datetime import date

from flask import Blueprint, render_template, request
from flask_login import login_required

from app.repositories import BillingRepository
from app.services import DashboardService

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


@billing_bp.get("/")
@login_required
def billing_list():
    year_month = request.args.get("month", date.today().strftime("%Y-%m"))
    bills = BillingRepository.list_for_month(year_month)
    summary = DashboardService.get_summary(year_month)
    return render_template(
        "billing/list.html",
        bills=bills,
        year_month=year_month,
        month_collected=summary["month_collected"],
        month_unpaid=summary["month_unpaid"],
    )
