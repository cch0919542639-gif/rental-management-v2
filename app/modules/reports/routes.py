from datetime import date

from flask import Blueprint, render_template, request
from flask_login import login_required

from app.modules.reports.forms import MaintenanceReportForm, ReportMonthForm, ReportYearForm
from app.repositories import PropertyRepository
from app.services import ReportService

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _populate_maintenance_property_choices(form: MaintenanceReportForm):
    form.property_id.choices = [(0, "全部")] + [(prop.id, prop.name) for prop in PropertyRepository.list_all()]


@reports_bp.get("/")
@login_required
def report_index():
    current_month = date.today().strftime("%Y-%m")
    current_year = date.today().year
    return render_template(
        "reports/index.html",
        current_month=current_month,
        current_year=current_year,
    )


@reports_bp.route("/monthly", methods=["GET", "POST"])
@login_required
def monthly_report():
    form = ReportMonthForm()
    year_month = request.args.get("year_month") or date.today().strftime("%Y-%m")
    if form.validate_on_submit():
        year_month = form.year_month.data.strip()
    else:
        form.year_month.data = year_month
    rows = ReportService.monthly_report(year_month)
    return render_template("reports/monthly.html", form=form, rows=rows, year_month=year_month)


@reports_bp.route("/landlord-summary", methods=["GET", "POST"])
@login_required
def landlord_summary():
    form = ReportMonthForm()
    year_month = request.args.get("year_month") or date.today().strftime("%Y-%m")
    if form.validate_on_submit():
        year_month = form.year_month.data.strip()
    else:
        form.year_month.data = year_month
    rows = ReportService.landlord_summary(year_month)
    return render_template("reports/landlord_summary.html", form=form, rows=rows, year_month=year_month)


@reports_bp.route("/yearly", methods=["GET", "POST"])
@login_required
def yearly_overview():
    form = ReportYearForm()
    year = request.args.get("year", type=int) or date.today().year
    if form.validate_on_submit():
        year = form.year.data
    else:
        form.year.data = year
    rows = ReportService.yearly_overview(year)
    return render_template("reports/yearly.html", form=form, rows=rows, year=year)


@reports_bp.route("/maintenance", methods=["GET", "POST"])
@login_required
def maintenance_summary():
    form = MaintenanceReportForm()
    _populate_maintenance_property_choices(form)
    if form.validate_on_submit():
        property_id = form.property_id.data or None
        status = (form.status.data or "").strip() or None
        reported_from = form.reported_from.data.isoformat() if form.reported_from.data else None
        reported_to = form.reported_to.data.isoformat() if form.reported_to.data else None
    else:
        property_id = request.args.get("property_id", type=int) or None
        status = (request.args.get("status") or "").strip() or None
        reported_from = request.args.get("reported_from", type=str) or None
        reported_to = request.args.get("reported_to", type=str) or None
        form.property_id.data = property_id or 0
        form.status.data = status or ""
    summary = ReportService.maintenance_summary(
        property_id=property_id,
        status=status,
        reported_from=reported_from,
        reported_to=reported_to,
    )
    return render_template("reports/maintenance.html", form=form, summary=summary)
