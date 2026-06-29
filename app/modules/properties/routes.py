from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.modules.properties.forms import PropertyForm
from app.repositories import LandlordRepository, PropertyRepository
from app.services import PropertyService

properties_bp = Blueprint("properties", __name__, url_prefix="/properties")


def _populate_landlord_choices(form: PropertyForm):
    form.landlord_id.choices = [(landlord.id, landlord.name) for landlord in LandlordRepository.list_all()]


def _populate_single_landlord_choice(form: PropertyForm, landlord_id: int):
    landlord = LandlordRepository.get_or_404(landlord_id)
    form.landlord_id.choices = [(landlord.id, landlord.name)]
    form.landlord_id.data = landlord.id
    return landlord


@properties_bp.get("/")
@login_required
def property_list():
    properties = PropertyRepository.list_all()
    return render_template("properties/list.html", properties=properties)


@properties_bp.route("/create", methods=["GET", "POST"])
@login_required
def property_create():
    form = PropertyForm()
    _populate_landlord_choices(form)
    if form.validate_on_submit():
        PropertyService.create_property(
            landlord_id=form.landlord_id.data,
            name=form.name.data.strip(),
            address=form.address.data,
            total_rooms=form.total_rooms.data,
            electricity_meter_type=form.electricity_meter_type.data,
            water_meter_type=form.water_meter_type.data,
            billing_rule=form.billing_rule.data,
        )
        flash("物件已建立", "success")
        return redirect(url_for("properties.property_list"))
    return render_template("properties/form.html", form=form, title="新增物件")


@properties_bp.route("/landlord/<int:landlord_id>/create", methods=["GET", "POST"])
@login_required
def property_create_for_landlord(landlord_id: int):
    form = PropertyForm()
    landlord = _populate_single_landlord_choice(form, landlord_id)
    if form.validate_on_submit():
        PropertyService.create_property(
            landlord_id=landlord.id,
            name=form.name.data.strip(),
            address=form.address.data,
            total_rooms=form.total_rooms.data,
            electricity_meter_type=form.electricity_meter_type.data,
            water_meter_type=form.water_meter_type.data,
            billing_rule=form.billing_rule.data,
        )
        flash("物件已建立", "success")
        return redirect(url_for("properties.property_list"))
    return render_template(
        "properties/form.html",
        form=form,
        title=f"為房東新增物件：{landlord.name}",
        parent_context=f"房東：{landlord.name}",
    )


@properties_bp.route("/<int:property_id>/edit", methods=["GET", "POST"])
@login_required
def property_edit(property_id: int):
    prop = PropertyRepository.get_or_404(property_id)
    form = PropertyForm(obj=prop)
    _populate_landlord_choices(form)
    if form.validate_on_submit():
        PropertyService.update_property(
            prop,
            landlord_id=form.landlord_id.data,
            name=form.name.data.strip(),
            address=form.address.data,
            total_rooms=form.total_rooms.data,
            electricity_meter_type=form.electricity_meter_type.data,
            water_meter_type=form.water_meter_type.data,
            billing_rule=form.billing_rule.data,
        )
        flash("物件已更新", "success")
        return redirect(url_for("properties.property_list"))
    return render_template("properties/form.html", form=form, title="編輯物件")
