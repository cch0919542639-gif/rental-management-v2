from datetime import date

from flask import Blueprint, abort, make_response, render_template, request
from flask_login import current_user, login_required

from app.modules.reports.forms import (
    MaintenanceReportForm,
    MoveOutSettlementReportForm,
    PropertyReportMonthForm,
    PropertyReportYearForm,
    ReportMonthForm,
    ReportYearForm,
)
from app.repositories import PropertyRepository
from app.services import ReportExportService, ReportService

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

OWNER_RELEASED_MONTHS = frozenset({"2026-05", "2026-06"})
OWNER_MONTHLY_ENDPOINTS = {
    "reports.monthly_report", "reports.monthly_report_export",
    "reports.landlord_summary", "reports.landlord_summary_export",
    "reports.collection_report", "reports.collection_report_export",
    "reports.property_settlement_report", "reports.property_settlement_report_export",
    "reports.property_expenses_report", "reports.property_expenses_report_export",
    "reports.move_out_settlements_report", "reports.move_out_settlements_report_export",
    "reports.new_tenants_report", "reports.new_tenants_report_export",
}
def _default_year_month():
    if not current_user.is_admin:
        return max(OWNER_RELEASED_MONTHS)
    return date.today().strftime("%Y-%m")


@reports_bp.before_request
def restrict_owner_report_period():
    if not current_user.is_authenticated or current_user.is_admin:
        return
    if request.endpoint in OWNER_MONTHLY_ENDPOINTS:
        year_month = request.values.get("year_month") or _default_year_month()
        if year_month not in OWNER_RELEASED_MONTHS:
            abort(403)


def _populate_maintenance_property_choices(form: MaintenanceReportForm):
    form.property_id.choices = [(0, "全部")] + [(prop.id, prop.name) for prop in PropertyRepository.list_all()]


def _visible_properties():
    properties = PropertyRepository.list_all()
    if current_user.is_admin:
        return properties
    if current_user.property_accesses:
        property_ids = {access.property_id for access in current_user.property_accesses}
        return [property_obj for property_obj in properties if property_obj.id in property_ids]
    return []


def _populate_property_choices(form, properties):
    form.property_ids.choices = [(prop.id, prop.name) for prop in properties]


def _selected_property_ids(form, visible_properties):
    visible_ids = {property_obj.id for property_obj in visible_properties}
    requested_ids = form.property_ids.data if request.method == "POST" else request.args.getlist("property_id", type=int)
    requested_ids = requested_ids or list(visible_ids)
    if not set(requested_ids).issubset(visible_ids):
        abort(403)
    return requested_ids


def _visible_property_ids():
    return [property_obj.id for property_obj in _visible_properties()]


def _download_export(*, rows: list[dict], headers: list[str], filename_base: str, export_format: str):
    payload = ReportExportService.export_rows(
        rows=rows,
        headers=headers,
        filename_base=filename_base,
        export_format=export_format,
    )
    response = make_response(payload.content)
    response.headers["Content-Type"] = payload.content_type
    response.headers["Content-Disposition"] = f'attachment; filename="{payload.filename}"'
    return response


@reports_bp.get("/")
@login_required
def report_index():
    current_month = _default_year_month()
    current_year = date.today().year
    return render_template(
        "reports/index.html",
        current_month=current_month,
        current_year=current_year,
        landlord_view=not current_user.is_admin,
    )


@reports_bp.route("/monthly", methods=["GET", "POST"])
@login_required
def monthly_report():
    form = ReportMonthForm()
    year_month = request.args.get("year_month") or _default_year_month()
    if form.validate_on_submit():
        year_month = form.year_month.data.strip()
    else:
        form.year_month.data = year_month
    rows = ReportService.monthly_report(year_month, _visible_property_ids())
    return render_template("reports/monthly.html", form=form, rows=rows, year_month=year_month)


@reports_bp.get("/monthly/export")
@login_required
def monthly_report_export():
    year_month = request.args.get("year_month") or _default_year_month()
    export_format = request.args.get("format") or "csv"
    rows = ReportService.monthly_report(year_month, _visible_property_ids())
    headers = [
        "year_month",
        "landlord_name",
        "property_name",
        "room_number",
        "tenant_name",
        "rent",
        "electricity_amount",
        "public_electricity",
        "electricity_usage",
        "water_amount",
        "water_usage",
        "other_charges",
        "other_desc",
        "total",
        "paid",
    ]
    return _download_export(rows=rows, headers=headers, filename_base=f"monthly-report-{year_month}", export_format=export_format)


@reports_bp.route("/landlord-summary", methods=["GET", "POST"])
@login_required
def landlord_summary():
    form = ReportMonthForm()
    year_month = request.args.get("year_month") or _default_year_month()
    if form.validate_on_submit():
        year_month = form.year_month.data.strip()
    else:
        form.year_month.data = year_month
    rows = ReportService.landlord_summary(year_month, _visible_property_ids())
    return render_template("reports/landlord_summary.html", form=form, rows=rows, year_month=year_month)


@reports_bp.get("/landlord-summary/export")
@login_required
def landlord_summary_export():
    year_month = request.args.get("year_month") or _default_year_month()
    export_format = request.args.get("format") or "csv"
    rows = ReportService.landlord_summary(year_month, _visible_property_ids())
    headers = [
        "landlord_id",
        "landlord_name",
        "property_id",
        "property_name",
        "bill_count",
        "total_amount",
        "paid_amount",
        "unpaid_amount",
    ]
    return _download_export(rows=rows, headers=headers, filename_base=f"landlord-summary-{year_month}", export_format=export_format)


@reports_bp.route("/yearly", methods=["GET", "POST"])
@login_required
def yearly_overview():
    form = ReportYearForm()
    year = request.args.get("year", type=int) or date.today().year
    if form.validate_on_submit():
        year = form.year.data
    else:
        form.year.data = year
    rows = ReportService.yearly_overview(year, _visible_property_ids())
    return render_template("reports/yearly.html", form=form, rows=rows, year=year)


@reports_bp.get("/yearly/export")
@login_required
def yearly_overview_export():
    year = request.args.get("year", type=int) or date.today().year
    export_format = request.args.get("format") or "csv"
    rows = ReportService.yearly_overview(year, _visible_property_ids())
    headers = [
        "year_month",
        "total_amount",
        "paid_amount",
        "unpaid_amount",
    ]
    rows = ReportService.export_money_rows(rows, ["total_amount", "paid_amount", "unpaid_amount"])
    return _download_export(rows=rows, headers=headers, filename_base=f"yearly-overview-{year}", export_format=export_format)


@reports_bp.route("/collection", methods=["GET", "POST"])
@login_required
def collection_report():
    form = PropertyReportMonthForm()
    visible_properties = _visible_properties()
    _populate_property_choices(form, visible_properties)
    year_month = request.args.get("year_month") or _default_year_month()
    if form.validate_on_submit():
        year_month = form.year_month.data.strip()
    else:
        form.year_month.data = year_month
        form.property_ids.data = request.args.getlist("property_id", type=int)
    property_ids = _selected_property_ids(form, visible_properties)
    rows = ReportService.property_collection(year_month, property_ids)
    return render_template(
        "reports/collection.html",
        form=form,
        rows=rows,
        year_month=year_month,
        selected_property_ids=property_ids,
        totals=ReportService.totals(
            rows,
            ["total", "paid_amount", "offset_adjustment", "balance_amount", "outstanding_amount"],
        ),
    )


@reports_bp.get("/collection/export")
@login_required
def collection_report_export():
    year_month = request.args.get("year_month") or _default_year_month()
    visible_properties = _visible_properties()
    property_ids = _selected_property_ids(PropertyReportMonthForm(meta={"csrf": False}), visible_properties)
    export_format = request.args.get("format") or "csv"
    rows = ReportService.property_collection(year_month, property_ids)
    headers = [
        "year_month", "landlord_name", "property_name", "room_number", "tenant_name", "tenant_phone",
        "contract_start_date", "contract_end_date",
        "rent", "electricity_amount", "public_electricity", "water_amount", "other_charges", "other_desc",
        "previous_balance", "total", "paid_amount", "outstanding_amount",
    ]
    rows = ReportService.export_money_rows(
        rows,
        [
            "rent", "electricity_amount", "public_electricity", "water_amount", "other_charges",
            "previous_balance", "total", "paid_amount", "outstanding_amount",
        ],
    )
    return _download_export(
        rows=rows,
        headers=headers,
        filename_base=f"property-collection-{year_month}",
        export_format=export_format,
    )


@reports_bp.route("/property-settlement", methods=["GET", "POST"])
@login_required
def property_settlement_report():
    form = PropertyReportMonthForm()
    visible_properties = _visible_properties()
    _populate_property_choices(form, visible_properties)
    year_month = request.args.get("year_month") or _default_year_month()
    if form.validate_on_submit():
        year_month = form.year_month.data.strip()
    else:
        form.year_month.data = year_month
        form.property_ids.data = request.args.getlist("property_id", type=int)
    property_ids = _selected_property_ids(form, visible_properties)
    rows = ReportService.property_settlement(year_month, property_ids)
    return render_template(
        "reports/property_settlement.html",
        form=form,
        rows=rows,
        year_month=year_month,
        selected_property_ids=property_ids,
        totals=ReportService.totals(
            rows,
            [
                "bill_count", "rent_amount", "electricity_amount", "public_electricity", "water_amount",
                "other_charges", "previous_balance", "total_amount", "paid_amount", "outstanding_amount",
                "expense_amount", "net_amount",
            ],
        ),
    )


@reports_bp.get("/property-settlement/export")
@login_required
def property_settlement_report_export():
    year_month = request.args.get("year_month") or _default_year_month()
    visible_properties = _visible_properties()
    property_ids = _selected_property_ids(PropertyReportMonthForm(meta={"csrf": False}), visible_properties)
    export_format = request.args.get("format") or "csv"
    rows = ReportService.property_settlement(year_month, property_ids)
    headers = [
        "landlord_name", "property_name", "bill_count", "rent_amount", "electricity_amount", "public_electricity",
        "water_amount", "other_charges", "previous_balance", "total_amount", "paid_amount", "outstanding_amount",
        "expense_amount", "net_amount",
    ]
    rows = ReportService.export_money_rows(
        rows,
        [
            "rent_amount", "electricity_amount", "public_electricity", "water_amount", "other_charges",
            "previous_balance", "total_amount", "paid_amount", "outstanding_amount", "expense_amount", "net_amount",
        ],
    )
    return _download_export(
        rows=rows,
        headers=headers,
        filename_base=f"property-settlement-{year_month}",
        export_format=export_format,
    )


@reports_bp.route("/property-expenses", methods=["GET", "POST"])
@login_required
def property_expenses_report():
    form = PropertyReportMonthForm()
    visible_properties = _visible_properties()
    _populate_property_choices(form, visible_properties)
    year_month = request.args.get("year_month") or _default_year_month()
    if form.validate_on_submit():
        year_month = form.year_month.data.strip()
    else:
        form.year_month.data = year_month
        form.property_ids.data = request.args.getlist("property_id", type=int)
    property_ids = _selected_property_ids(form, visible_properties)
    rows = ReportService.property_expenses(year_month, property_ids)
    return render_template(
        "reports/property_expenses.html",
        form=form,
        rows=rows,
        year_month=year_month,
        selected_property_ids=property_ids,
        totals=ReportService.totals(rows, ["amount"]),
    )


@reports_bp.get("/property-expenses/export")
@login_required
def property_expenses_report_export():
    year_month = request.args.get("year_month") or _default_year_month()
    visible_properties = _visible_properties()
    property_ids = _selected_property_ids(PropertyReportMonthForm(meta={"csrf": False}), visible_properties)
    export_format = request.args.get("format") or "csv"
    rows = ReportService.property_expenses(year_month, property_ids)
    headers = [
        "transaction_date", "landlord_name", "property_name", "category", "amount", "payee", "reference_no", "notes",
    ]
    rows = ReportService.export_money_rows(rows, ["amount"])
    return _download_export(
        rows=rows,
        headers=headers,
        filename_base=f"property-expenses-{year_month}",
        export_format=export_format,
    )


@reports_bp.route("/move-out-settlements", methods=["GET", "POST"])
@login_required
def move_out_settlements_report():
    form = MoveOutSettlementReportForm()
    landlord_view = not current_user.is_admin
    if landlord_view:
        form.status.choices = [("", "全部"), ("settled", "已結算"), ("unsettled", "未結算")]
    visible_properties = _visible_properties()
    _populate_property_choices(form, visible_properties)
    year_month = request.args.get("year_month") or date.today().strftime("%Y-%m")
    status = (request.args.get("status") or "").strip()
    if form.validate_on_submit():
        year_month = form.year_month.data.strip()
        status = (form.status.data or "").strip()
    else:
        form.year_month.data = year_month
        form.status.data = status
        form.property_ids.data = request.args.getlist("property_id", type=int)
    if landlord_view and status not in {"", "settled", "unsettled"}:
        abort(403)
    property_ids = _selected_property_ids(form, visible_properties)
    rows = ReportService.move_out_settlements(year_month, property_ids, status)
    money_fields = ["deposit_held", "refund_amount", "gross_charges", "allocated_amount", "outstanding_amount", "suggested_cash_refund"]
    return render_template(
        "reports/move_out_settlements.html", form=form, rows=rows, year_month=year_month, status=status,
        selected_property_ids=property_ids, totals=ReportService.totals(rows, money_fields), landlord_view=landlord_view,
    )


@reports_bp.get("/move-out-settlements/export")
@login_required
def move_out_settlements_report_export():
    year_month = request.args.get("year_month") or date.today().strftime("%Y-%m")
    status = (request.args.get("status") or "").strip()
    visible_properties = _visible_properties()
    landlord_view = not current_user.is_admin
    if landlord_view and status not in {"", "settled", "unsettled"}:
        abort(403)
    property_ids = _selected_property_ids(MoveOutSettlementReportForm(meta={"csrf": False}), visible_properties)
    export_format = request.args.get("format") or "csv"
    rows = ReportService.move_out_settlements(year_month, property_ids, status)
    headers = [
        "settlement_id", "move_out_date", "status", "landlord_name", "property_name", "room_number", "tenant_name", "tenant_phone",
        "deposit_held", "refund_amount", "final_rent", "electricity_amount", "water_amount", "management_fee", "previous_debt",
        "cleaning_fee", "repair_fee", "other_charge", "other_desc", "gross_charges", "allocated_amount", "outstanding_amount",
        "suggested_cash_refund", "evidence_type", "evidence_reference",
    ]
    if landlord_view:
        headers[2:3] = ["landlord_status", "unsettled_reason"]
    rows = ReportService.export_money_rows(rows, [
        "deposit_held", "refund_amount", "final_rent", "electricity_amount", "water_amount", "management_fee", "previous_debt",
        "cleaning_fee", "repair_fee", "other_charge", "gross_charges", "allocated_amount", "outstanding_amount", "suggested_cash_refund",
    ])
    return _download_export(
        rows=rows, headers=headers, filename_base=f"move-out-settlements-{year_month}", export_format=export_format,
    )


@reports_bp.route("/new-tenants", methods=["GET", "POST"])
@login_required
def new_tenants_report():
    form = PropertyReportMonthForm()
    visible_properties = _visible_properties()
    _populate_property_choices(form, visible_properties)
    year_month = request.args.get("year_month") or date.today().strftime("%Y-%m")
    if form.validate_on_submit():
        year_month = form.year_month.data.strip()
    else:
        form.year_month.data = year_month
        form.property_ids.data = request.args.getlist("property_id", type=int)
    property_ids = _selected_property_ids(form, visible_properties)
    rows = ReportService.new_tenants(year_month, property_ids)
    return render_template(
        "reports/new_tenants.html",
        form=form,
        rows=rows,
        year_month=year_month,
        selected_property_ids=property_ids,
    )


@reports_bp.get("/new-tenants/export")
@login_required
def new_tenants_report_export():
    year_month = request.args.get("year_month") or date.today().strftime("%Y-%m")
    visible_properties = _visible_properties()
    property_ids = _selected_property_ids(PropertyReportMonthForm(meta={"csrf": False}), visible_properties)
    export_format = request.args.get("format") or "csv"
    rows = ReportService.new_tenants(year_month, property_ids)
    headers = [
        "property_name", "room_number", "tenant_name", "tenant_phone", "start_date", "end_date", "deposit", "rent",
        "start_electricity_reading", "start_water_reading", "contract_status", "notes",
    ]
    rows = ReportService.export_money_rows(rows, ["deposit", "rent"])
    return _download_export(
        rows=rows,
        headers=headers,
        filename_base=f"new-tenants-{year_month}",
        export_format=export_format,
    )


@reports_bp.route("/property-yearly", methods=["GET", "POST"])
@login_required
def property_yearly_report():
    form = PropertyReportYearForm()
    visible_properties = _visible_properties()
    _populate_property_choices(form, visible_properties)
    year = request.args.get("year", type=int) or date.today().year
    if form.validate_on_submit():
        year = form.year.data
    else:
        form.year.data = year
        form.property_ids.data = request.args.getlist("property_id", type=int)
    property_ids = _selected_property_ids(form, visible_properties)
    rows = ReportService.property_yearly(year, property_ids)
    return render_template(
        "reports/property_yearly.html",
        form=form,
        rows=rows,
        year=year,
        selected_property_ids=property_ids,
        totals=ReportService.totals(
            rows,
            [
                "bill_count", "rent_amount", "electricity_amount", "public_electricity", "water_amount",
                "other_charges", "previous_balance", "total_amount", "paid_amount", "outstanding_amount",
            ],
        ),
    )


@reports_bp.get("/property-yearly/export")
@login_required
def property_yearly_report_export():
    year = request.args.get("year", type=int) or date.today().year
    visible_properties = _visible_properties()
    property_ids = _selected_property_ids(PropertyReportYearForm(meta={"csrf": False}), visible_properties)
    export_format = request.args.get("format") or "csv"
    rows = ReportService.property_yearly(year, property_ids)
    headers = [
        "year_month", "property_name", "bill_count", "rent_amount", "electricity_amount", "public_electricity",
        "water_amount", "other_charges", "previous_balance", "total_amount", "paid_amount", "outstanding_amount",
    ]
    rows = ReportService.export_money_rows(
        rows,
        [
            "rent_amount", "electricity_amount", "public_electricity", "water_amount", "other_charges",
            "previous_balance", "total_amount", "paid_amount", "outstanding_amount",
        ],
    )
    return _download_export(
        rows=rows,
        headers=headers,
        filename_base=f"property-yearly-{year}",
        export_format=export_format,
    )


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
