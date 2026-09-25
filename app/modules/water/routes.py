from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.core.errors import ConflictError
from app.models.billing import UtilityCalculationDraft
from app.modules.water.forms import WaterBillForm, WaterPostForm
from app.repositories import PropertyRepository, WaterBillRepository
from app.services import WaterService
from app.services.utility_draft_service import UtilityDraftService

water_bp = Blueprint("water", __name__, url_prefix="/water")


def _populate_property_choices(form: WaterBillForm):
    form.property_id.choices = [(prop.id, prop.name) for prop in PropertyRepository.list_all()]


@water_bp.get("/")
@login_required
def water_list():
    water_bills = WaterBillRepository.list_all()
    return render_template("water/list.html", water_bills=water_bills)


@water_bp.route("/create", methods=["GET", "POST"])
@login_required
def water_create():
    form = WaterBillForm()
    _populate_property_choices(form)
    if form.validate_on_submit():
        WaterService.create_water_bill(
            property_id=form.property_id.data,
            billing_start=form.billing_start.data,
            billing_end=form.billing_end.data,
            total_amount=form.total_amount.data,
            meter_prev_1=form.meter_prev_1.data,
            meter_curr_1=form.meter_curr_1.data,
            sub_meter_1=form.sub_meter_1.data,
            actual_usage_1=form.actual_usage_1.data,
            meter_prev_2=form.meter_prev_2.data,
            meter_curr_2=form.meter_curr_2.data,
            sub_meter_2=form.sub_meter_2.data,
            actual_usage_2=form.actual_usage_2.data,
            notes=form.notes.data,
        )
        flash("水費單已建立", "success")
        return redirect(url_for("water.water_list"))
    return render_template("water/form.html", form=form, title="新增水費單")


@water_bp.route("/<int:water_bill_id>/edit", methods=["GET", "POST"])
@login_required
def water_edit(water_bill_id: int):
    water_bill = WaterBillRepository.get_or_404(water_bill_id)
    form = WaterBillForm(obj=water_bill)
    _populate_property_choices(form)
    if form.validate_on_submit():
        WaterService.update_water_bill(
            water_bill,
            property_id=form.property_id.data,
            billing_start=form.billing_start.data,
            billing_end=form.billing_end.data,
            total_amount=form.total_amount.data,
            meter_prev_1=form.meter_prev_1.data,
            meter_curr_1=form.meter_curr_1.data,
            sub_meter_1=form.sub_meter_1.data,
            actual_usage_1=form.actual_usage_1.data,
            meter_prev_2=form.meter_prev_2.data,
            meter_curr_2=form.meter_curr_2.data,
            sub_meter_2=form.sub_meter_2.data,
            actual_usage_2=form.actual_usage_2.data,
            notes=form.notes.data,
        )
        flash("水費單已更新", "success")
        return redirect(url_for("water.water_list"))
    return render_template("water/form.html", form=form, title="編輯水費單")


@water_bp.route("/<int:water_bill_id>/post", methods=["GET", "POST"])
@login_required
def water_post(water_bill_id: int):
    water_bill = WaterBillRepository.get_or_404(water_bill_id)
    form = WaterPostForm()
    if form.validate_on_submit():
        if form.mode.data == "auto_policy":
            WaterService.post_policy_to_monthly_bill(
                monthly_bill_id=form.monthly_bill_id.data,
                water_bill=water_bill,
            )
        elif form.mode.data == "shared_by_stay_days":
            WaterService.post_shared_to_monthly_bill(
                monthly_bill_id=form.monthly_bill_id.data,
                water_bill=water_bill,
            )
        else:
            WaterService.post_independent_to_monthly_bill(
                monthly_bill_id=form.monthly_bill_id.data,
                water_bill=water_bill,
                amount=form.amount.data,
            )
        flash("水費已回寫月帳單", "success")
        return redirect(url_for("water.water_list"))
    return render_template("water/post_form.html", form=form, water_bill=water_bill, title="回寫月帳單")


@water_bp.route("/<int:water_bill_id>/preview", methods=["GET", "POST"])
@login_required
def water_preview(water_bill_id: int):
    water_bill = WaterBillRepository.get_or_404(water_bill_id)
    form = WaterPostForm()
    preview = None
    if form.validate_on_submit():
        preview = WaterService.preview_post_to_monthly_bill(
            monthly_bill_id=form.monthly_bill_id.data,
            water_bill=water_bill,
            mode=form.mode.data,
            amount=form.amount.data,
        )
    return render_template(
        "water/preview.html",
        form=form,
        water_bill=water_bill,
        preview=preview,
        title="水費預覽",
    )


@water_bp.get("/<int:water_bill_id>/property-preview")
@login_required
def water_property_preview(water_bill_id: int):
    water_bill = WaterBillRepository.get_or_404(water_bill_id)
    preview = WaterService.preview_property_shared_by_stay_days(water_bill=water_bill)
    draft = None
    draft_id = request.args.get("draft_id", type=int)
    if draft_id:
        draft = UtilityCalculationDraft.query.filter_by(id=draft_id, water_bill_id=water_bill.id).one_or_none()
    return render_template("water/property_preview.html", preview=preview, draft=draft, title="水費全物件分攤預覽")


@water_bp.post("/<int:water_bill_id>/property-draft")
@login_required
def water_property_draft_create(water_bill_id: int):
    water_bill = WaterBillRepository.get_or_404(water_bill_id)
    draft = WaterService.create_property_draft(water_bill=water_bill, year_month=request.form.get("year_month", ""))
    flash(f"已建立水費草稿 #{draft.id}，請核對後確認。", "success")
    return redirect(url_for("water.water_property_preview", water_bill_id=water_bill.id, draft_id=draft.id))


@water_bp.post("/<int:water_bill_id>/drafts/<int:draft_id>/confirm")
@login_required
def water_property_draft_confirm(water_bill_id: int, draft_id: int):
    draft = UtilityCalculationDraft.query.filter_by(id=draft_id, water_bill_id=water_bill_id).one_or_404()
    UtilityDraftService.confirm(draft)
    flash(f"水費草稿 #{draft.id} 已確認，可回寫對應月帳單。", "success")
    return redirect(url_for("water.water_property_preview", water_bill_id=water_bill_id, draft_id=draft.id))


@water_bp.post("/<int:water_bill_id>/delete")
@login_required
def water_delete(water_bill_id: int):
    water_bill = WaterBillRepository.get_or_404(water_bill_id)
    try:
        WaterService.delete_water_bill(water_bill)
        flash("水費單已刪除", "success")
    except ConflictError as exc:
        flash(exc.message, "error")
    return redirect(url_for("water.water_list"))
