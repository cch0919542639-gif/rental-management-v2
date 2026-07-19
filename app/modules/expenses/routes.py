from flask import Blueprint, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.modules.expenses.forms import PropertyExpenseForm
from app.repositories import PropertyExpenseRepository, PropertyRepository
from app.services import PropertyExpenseService, ReportExportService

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")


def _populate_properties(form):
    form.property_id.choices = [(item.id, item.name) for item in PropertyRepository.list_all()]


@expenses_bp.get("/")
@login_required
def expense_list():
    property_id = request.args.get("property_id", type=int)
    status = request.args.get("status") or None
    category = request.args.get("category") or None
    expenses = PropertyExpenseRepository.list_filtered(property_id=property_id, status=status, category=category)
    return render_template(
        "expenses/list.html",
        expenses=expenses,
        posted_total=PropertyExpenseRepository.posted_total(),
        properties=PropertyRepository.list_all(), selected_property_id=property_id, selected_status=status, selected_category=category,
    )


@expenses_bp.route("/create", methods=["GET", "POST"])
@login_required
def expense_create():
    form = PropertyExpenseForm()
    _populate_properties(form)
    if form.validate_on_submit():
        PropertyExpenseService.create(
            property_id=form.property_id.data,
            transaction_date=form.transaction_date.data,
            category=form.category.data,
            amount=form.amount.data,
            payee=form.payee.data,
            reference_no=form.reference_no.data,
            notes=form.notes.data,
            created_by_id=current_user.id,
        )
        flash("支出草稿已建立", "success")
        return redirect(url_for("expenses.expense_list"))
    return render_template("expenses/form.html", form=form, title="新增物件支出")


@expenses_bp.route("/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def expense_edit(expense_id):
    expense = PropertyExpenseRepository.get_or_404(expense_id)
    form = PropertyExpenseForm(obj=expense)
    _populate_properties(form)
    if form.validate_on_submit():
        try:
            PropertyExpenseService.update(expense, **{name: getattr(form, name).data for name in PropertyExpenseService.DRAFT_FIELDS})
            flash("支出草稿已更新", "success")
            return redirect(url_for("expenses.expense_list"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("expenses/form.html", form=form, title="編輯支出草稿")


@expenses_bp.post("/<int:expense_id>/post")
@login_required
def expense_post(expense_id):
    expense = PropertyExpenseRepository.get_or_404(expense_id)
    try:
        PropertyExpenseService.transition(expense, "posted")
        flash("支出已入帳", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("expenses.expense_list"))


@expenses_bp.post("/<int:expense_id>/void")
@login_required
def expense_void(expense_id):
    expense = PropertyExpenseRepository.get_or_404(expense_id)
    reason = (request.form.get("void_reason") or "").strip()
    try:
        PropertyExpenseService.transition(expense, "voided", void_reason=reason)
        flash("支出已作廢", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("expenses.expense_list"))


@expenses_bp.get("/export")
@login_required
def expense_export():
    rows = [{"transaction_date": str(item.transaction_date), "property_name": item.property.name, "category": item.category, "amount": int(item.amount or 0), "payee": item.payee or "", "reference_no": item.reference_no or "", "record_status": item.record_status} for item in PropertyExpenseRepository.list_filtered(status="posted")]
    payload = ReportExportService.export_rows(rows=rows, headers=list(rows[0]) if rows else ["transaction_date", "property_name", "category", "amount", "payee", "reference_no", "record_status"], filename_base="property-expenses", export_format=request.args.get("format") or "csv")
    response = make_response(payload.content)
    response.headers["Content-Type"] = payload.content_type
    response.headers["Content-Disposition"] = f'attachment; filename="{payload.filename}"'
    return response


@expenses_bp.post("/<int:expense_id>/delete")
@login_required
def expense_delete(expense_id):
    expense = PropertyExpenseRepository.get_or_404(expense_id)
    try:
        PropertyExpenseService.delete(expense)
        flash("支出草稿已刪除", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("expenses.expense_list"))
