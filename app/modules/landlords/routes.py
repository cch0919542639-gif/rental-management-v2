from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.modules.landlords.forms import LandlordForm
from app.repositories import LandlordRepository
from app.services import LandlordService

landlords_bp = Blueprint("landlords", __name__, url_prefix="/landlords")


@landlords_bp.get("/")
@login_required
def landlord_list():
    landlords = LandlordRepository.list_all()
    return render_template("landlords/list.html", landlords=landlords)


@landlords_bp.route("/create", methods=["GET", "POST"])
@login_required
def landlord_create():
    form = LandlordForm()
    if form.validate_on_submit():
        LandlordService.create_landlord(
            name=form.name.data.strip(),
            phone=form.phone.data,
            electricity_account=form.electricity_account.data,
            water_account=form.water_account.data,
            electricity_rate_type=form.electricity_rate_type.data,
            electricity_rate=form.electricity_rate.data,
            water_rate_type=form.water_rate_type.data,
            water_rate=form.water_rate.data,
            notes=form.notes.data,
        )
        flash("房東已建立", "success")
        return redirect(url_for("landlords.landlord_list"))
    return render_template("landlords/form.html", form=form, title="新增房東")


@landlords_bp.route("/<int:landlord_id>/edit", methods=["GET", "POST"])
@login_required
def landlord_edit(landlord_id: int):
    landlord = LandlordRepository.get_or_404(landlord_id)
    form = LandlordForm(obj=landlord)
    if form.validate_on_submit():
        LandlordService.update_landlord(
            landlord,
            name=form.name.data.strip(),
            phone=form.phone.data,
            electricity_account=form.electricity_account.data,
            water_account=form.water_account.data,
            electricity_rate_type=form.electricity_rate_type.data,
            electricity_rate=form.electricity_rate.data,
            water_rate_type=form.water_rate_type.data,
            water_rate=form.water_rate.data,
            notes=form.notes.data,
        )
        flash("房東已更新", "success")
        return redirect(url_for("landlords.landlord_list"))
    return render_template("landlords/form.html", form=form, title="編輯房東")
