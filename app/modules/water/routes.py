from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.core.errors import ConflictError
from app.modules.water.forms import WaterBillForm, WaterPostForm
from app.repositories import PropertyRepository, WaterBillRepository
from app.services import WaterService

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
        if form.mode.data == "shared_by_stay_days":
            WaterService.post_shared_to_monthly_bill(
                monthly_bill_id=form.monthly_bill_id.data,
                water_bill=water_bill,
            )
        else:
            WaterService.post_independent_to_monthly_bill(
                monthly_bill_id=form.monthly_bill_id.data,
                amount=form.amount.data,
            )
        flash("水費已回寫月帳單", "success")
        return redirect(url_for("water.water_list"))
    return render_template("water/post_form.html", form=form, water_bill=water_bill, title="回寫月帳單")


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
