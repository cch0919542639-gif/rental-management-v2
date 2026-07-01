from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.core.errors import DomainValidationError
from app.core.security import admin_required
from app.modules.billing.forms import BillingGenerateForm, MonthlyBillForm
from app.repositories import BillingRepository, ContractRepository
from app.services import BillingGenerationService, DashboardService

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


def _populate_contract_choices(form: MonthlyBillForm):
    form.contract_id.choices = [
        (contract.id, f"{contract.tenant.name} / {contract.room.property.name} / {contract.room.room_number}")
        for contract in ContractRepository.list_all()
    ]


@billing_bp.get("/")
@login_required
def billing_list():
    year_month = request.args.get("month") or request.args.get("year_month") or date.today().strftime("%Y-%m")
    try:
        bills = BillingRepository.list_for_month(year_month)
        summary = DashboardService.get_summary(year_month)
    except ValueError as exc:
        raise DomainValidationError("月份格式錯誤", details={"year_month": [str(exc)]}) from exc
    return render_template(
        "billing/list.html",
        bills=bills,
        year_month=year_month,
        month_collected=summary["month_collected"],
        month_unpaid=summary["month_unpaid"],
    )


@billing_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def billing_create():
    form = MonthlyBillForm()
    _populate_contract_choices(form)
    if form.validate_on_submit():
        BillingGenerationService.create_monthly_bill(
            contract_id=form.contract_id.data,
            year_month=form.year_month.data.strip(),
            rent=form.rent.data,
            electricity_prev=form.electricity_prev.data,
            electricity_curr=form.electricity_curr.data,
            electricity_usage=form.electricity_usage.data,
            electricity_amount=form.electricity_amount.data,
            public_electricity=form.public_electricity.data,
            water_prev=form.water_prev.data,
            water_curr=form.water_curr.data,
            water_usage=form.water_usage.data,
            water_amount=form.water_amount.data,
            other_charges=form.other_charges.data,
            other_desc=form.other_desc.data,
            paid=form.paid.data,
            notes=form.notes.data,
        )
        flash("月帳單已建立", "success")
        return redirect(url_for("billing.billing_list", year_month=form.year_month.data.strip()))
    return render_template("billing/form.html", form=form, title="新增月帳單")


@billing_bp.route("/<int:monthly_bill_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def billing_edit(monthly_bill_id: int):
    bill = BillingRepository.get_or_404(monthly_bill_id)
    form = MonthlyBillForm(obj=bill)
    if request.method == "GET":
        form.year_month.data = bill.year_month[:4] + "-" + bill.year_month[4:]
    _populate_contract_choices(form)
    if form.validate_on_submit():
        BillingGenerationService.update_monthly_bill(
            bill,
            contract_id=form.contract_id.data,
            year_month=form.year_month.data.strip(),
            rent=form.rent.data,
            electricity_prev=form.electricity_prev.data,
            electricity_curr=form.electricity_curr.data,
            electricity_usage=form.electricity_usage.data,
            electricity_amount=form.electricity_amount.data,
            public_electricity=form.public_electricity.data,
            water_prev=form.water_prev.data,
            water_curr=form.water_curr.data,
            water_usage=form.water_usage.data,
            water_amount=form.water_amount.data,
            other_charges=form.other_charges.data,
            other_desc=form.other_desc.data,
            paid=form.paid.data,
            notes=form.notes.data,
        )
        flash("月帳單已更新", "success")
        return redirect(url_for("billing.billing_list", year_month=form.year_month.data.strip()))
    return render_template("billing/form.html", form=form, title="編輯月帳單")


@billing_bp.post("/<int:monthly_bill_id>/toggle-paid")
@login_required
@admin_required
def billing_toggle_paid(monthly_bill_id: int):
    bill = BillingRepository.get_or_404(monthly_bill_id)
    BillingGenerationService.toggle_paid(bill)
    flash("月帳單付款狀態已更新", "success")
    return redirect(url_for("billing.billing_list", year_month=bill.year_month[:4] + "-" + bill.year_month[4:]))


@billing_bp.get("/contracts/<int:contract_id>")
@login_required
def billing_contract_list(contract_id: int):
    contract = ContractRepository.get_or_404(contract_id)
    bills = BillingRepository.list_for_contract(contract_id)
    return render_template("billing/contract_list.html", contract=contract, bills=bills)


@billing_bp.route("/contracts/<int:contract_id>/generate", methods=["GET", "POST"])
@login_required
@admin_required
def billing_contract_generate(contract_id: int):
    contract = ContractRepository.get_or_404(contract_id)
    form = BillingGenerateForm()
    form.contract_id.data = contract_id
    form.contract_id.render_kw = {"readonly": True}
    if request.method == "GET":
        form.year_month.data = date.today().strftime("%Y-%m")
    if form.validate_on_submit():
        bill, changed = BillingGenerationService.generate_for_contract(
            contract_id=contract_id,
            year_month=form.year_month.data.strip(),
            overwrite_existing=form.overwrite_existing.data,
        )
        flash("月帳單已產生" if changed else "該月份帳單已存在，未覆蓋", "success")
        return redirect(url_for("billing.billing_contract_list", contract_id=contract.id))
    return render_template("billing/generate_form.html", form=form, title="依合約產生月帳單", contract=contract)


@billing_bp.route("/batch", methods=["GET", "POST"])
@login_required
@admin_required
def billing_batch_generate():
    form = BillingGenerateForm()
    if request.method == "GET":
        form.year_month.data = date.today().strftime("%Y-%m")
    if form.validate_on_submit():
        result = BillingGenerationService.generate_for_month(
            year_month=form.year_month.data.strip(),
            overwrite_existing=form.overwrite_existing.data,
        )
        flash(
            f"批次完成：created_or_updated={len(result['created_or_updated_ids'])}, skipped={len(result['skipped_ids'])}",
            "success",
        )
        return redirect(url_for("billing.billing_list", year_month=form.year_month.data.strip()))
    return render_template("billing/generate_form.html", form=form, title="批次產生月帳單", contract=None)
