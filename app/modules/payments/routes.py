from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.core.security import admin_required
from app.modules.payments.forms import PaymentCreateForm, PaymentLinkForm, PaymentReviewForm
from app.repositories import BillingRepository, PaymentRepository
from app.services import PaymentService

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


def _populate_bill_choices(form):
    form.monthly_bill_id.choices = [(0, "未指定")] + [
        (bill.id, f"{bill.year_month} / Contract {bill.contract_id} / Total {bill.total}") for bill in BillingRepository.list_all()
    ]


@payments_bp.get("/")
@login_required
def payment_list():
    payments = PaymentRepository.list_all()
    return render_template("payments/list.html", payments=payments)


@payments_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def payment_create():
    form = PaymentCreateForm()
    _populate_bill_choices(form)
    if form.validate_on_submit():
        monthly_bill_id = form.monthly_bill_id.data or None
        PaymentService.create_payment_record(
            contract_id=form.contract_id.data or None,
            monthly_bill_id=monthly_bill_id,
            amount=form.amount.data,
            bank_name=form.bank_name.data,
            account_number=form.account_number.data,
            account_holder=form.account_holder.data,
            transaction_date=form.transaction_date.data,
            payer_name=form.payer_name.data,
            transaction_id=form.transaction_id.data,
            status_text=form.status_text.data,
            raw_ocr_text=form.raw_ocr_text.data,
            raw_llm_response=form.raw_llm_response.data,
            image_path=form.image_path.data,
            ocr_engine=form.ocr_engine.data,
            notes=form.notes.data,
        )
        flash("付款記錄已建立", "success")
        return redirect(url_for("payments.payment_list"))
    return render_template("payments/form.html", form=form, title="新增付款記錄")


@payments_bp.route("/<int:payment_id>/verify", methods=["GET", "POST"])
@login_required
@admin_required
def payment_verify(payment_id: int):
    record = PaymentRepository.get_or_404(payment_id)
    form = PaymentReviewForm(obj=record)
    if form.validate_on_submit():
        PaymentService.verify_payment(record, verified_by=current_user, notes=form.notes.data)
        flash("付款記錄已驗證", "success")
        return redirect(url_for("payments.payment_list"))
    return render_template("payments/review_form.html", form=form, record=record, title="驗證付款記錄")


@payments_bp.route("/<int:payment_id>/reject", methods=["GET", "POST"])
@login_required
@admin_required
def payment_reject(payment_id: int):
    record = PaymentRepository.get_or_404(payment_id)
    form = PaymentReviewForm(obj=record)
    if form.validate_on_submit():
        PaymentService.reject_payment(record, verified_by=current_user, notes=form.notes.data)
        flash("付款記錄已駁回", "success")
        return redirect(url_for("payments.payment_list"))
    return render_template("payments/review_form.html", form=form, record=record, title="駁回付款記錄")


@payments_bp.route("/<int:payment_id>/link", methods=["GET", "POST"])
@login_required
@admin_required
def payment_link(payment_id: int):
    record = PaymentRepository.get_or_404(payment_id)
    form = PaymentLinkForm()
    form.monthly_bill_id.choices = [
        (bill.id, f"{bill.year_month} / Contract {bill.contract_id} / Total {bill.total}") for bill in BillingRepository.list_all()
    ]
    if form.validate_on_submit():
        PaymentService.link_payment(
            record,
            monthly_bill_id=form.monthly_bill_id.data,
            verified_by=current_user,
            notes=form.notes.data,
        )
        flash("付款記錄已連結帳單", "success")
        return redirect(url_for("payments.payment_list"))
    return render_template("payments/link_form.html", form=form, record=record, title="連結付款記錄")
