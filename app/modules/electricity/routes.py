from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.modules.electricity.forms import (
    ElectricityBillForm,
    ElectricityMeterForm,
    ElectricityPostForm,
    ElectricityReadingForm,
)
from app.repositories import (
    CalcMethodRepository,
    ElectricityBillRepository,
    ElectricityMeterRepository,
    ElectricityReadingRepository,
    PropertyRepository,
    RoomRepository,
)
from app.services import ElectricityService

electricity_bp = Blueprint("electricity", __name__, url_prefix="/electricity")


def _populate_meter_form(form: ElectricityMeterForm):
    form.property_id.choices = [(prop.id, prop.name) for prop in PropertyRepository.list_all()]
    form.room_id.choices = [(0, "未指定")] + [
        (room.id, f"{room.property.name} / {room.room_number}") for room in RoomRepository.list_all()
    ]


def _populate_bill_form(form: ElectricityBillForm):
    form.property_id.choices = [(prop.id, prop.name) for prop in PropertyRepository.list_all()]
    form.meter_id.choices = [(0, "未指定")] + [
        (meter.id, f"Meter {meter.id} / Property {meter.property_id}") for meter in ElectricityMeterRepository.list_all()
    ]
    form.calc_method_id.choices = [(0, "未指定")] + [
        (item.id, item.name) for item in CalcMethodRepository.list_active()
    ]


def _populate_reading_form(form: ElectricityReadingForm):
    form.meter_id.choices = [
        (meter.id, f"Meter {meter.id} / Property {meter.property_id}") for meter in ElectricityMeterRepository.list_all()
    ]
    form.room_id.choices = [(0, "未指定")] + [
        (room.id, f"{room.property.name} / {room.room_number}") for room in RoomRepository.list_all()
    ]


@electricity_bp.get("/")
@login_required
def electricity_dashboard():
    bills = ElectricityBillRepository.list_all()
    meters = ElectricityMeterRepository.list_all()
    return render_template("electricity/index.html", bills=bills, meters=meters)
@electricity_bp.get("/property/<int:property_id>/bills")
@login_required
def property_bills(property_id: int):
    property_obj = PropertyRepository.get_or_404(property_id)
    bills = ElectricityBillRepository.list_by_property(property_id)
    meters = ElectricityMeterRepository.list_all()
    return render_template(
        "electricity/property_bills.html",
        bills=bills,
        meters=meters,
        property_obj=property_obj,
    )




@electricity_bp.route("/meters/create", methods=["GET", "POST"])
@login_required
def meter_create():
    form = ElectricityMeterForm()
    _populate_meter_form(form)
    if form.validate_on_submit():
        room_id = form.room_id.data or None
        ElectricityService.create_meter(
            property_id=form.property_id.data,
            room_id=room_id,
            meter_number=form.meter_number.data,
            room_number=form.room_number.data,
            is_main=form.is_main.data,
            notes=form.notes.data,
        )
        flash("電表已建立", "success")
        return redirect(url_for("electricity.electricity_dashboard"))
    return render_template("electricity/meter_form.html", form=form, title="新增電表")


@electricity_bp.route("/meters/<int:meter_id>/edit", methods=["GET", "POST"])
@login_required
def meter_edit(meter_id: int):
    meter = ElectricityMeterRepository.get_or_404(meter_id)
    form = ElectricityMeterForm(obj=meter)
    _populate_meter_form(form)
    if form.validate_on_submit():
        ElectricityService.update_meter(
            meter,
            property_id=form.property_id.data,
            room_id=form.room_id.data or None,
            meter_number=form.meter_number.data,
            room_number=form.room_number.data,
            is_main=form.is_main.data,
            notes=form.notes.data,
        )
        flash("電表已更新", "success")
        return redirect(url_for("electricity.electricity_dashboard"))
    return render_template("electricity/meter_form.html", form=form, title="編輯電表")


@electricity_bp.route("/bills/create", methods=["GET", "POST"])
@login_required
def bill_create():
    form = ElectricityBillForm()
    _populate_bill_form(form)
    if form.validate_on_submit():
        ElectricityService.create_bill(
            property_id=form.property_id.data,
            meter_id=form.meter_id.data or None,
            calc_method_id=form.calc_method_id.data or None,
            year_month=form.year_month.data.strip(),
            period_start=form.period_start.data,
            period_end=form.period_end.data,
            prev_reading=form.prev_reading.data,
            curr_reading=form.curr_reading.data,
            total_amount=form.total_amount.data,
            public_amount=form.public_amount.data,
            flow_amount=form.flow_amount.data,
            ocr_raw_text=form.ocr_raw_text.data,
            notes=form.notes.data,
        )
        flash("電費單已建立", "success")
        return redirect(url_for("electricity.electricity_dashboard"))
    return render_template("electricity/bill_form.html", form=form, title="新增電費單")


@electricity_bp.route("/bills/<int:bill_id>/readings/create", methods=["GET", "POST"])
@login_required
def reading_create(bill_id: int):
    bill = ElectricityBillRepository.get_or_404(bill_id)
    form = ElectricityReadingForm()
    _populate_reading_form(form)
    if form.validate_on_submit():
        ElectricityService.add_reading(
            bill,
            meter_id=form.meter_id.data,
            room_id=form.room_id.data or None,
            prev_reading=form.prev_reading.data,
            curr_reading=form.curr_reading.data,
            calculated_amount=form.calculated_amount.data,
            confirmed_amount=form.confirmed_amount.data,
            notes=form.notes.data,
        )
        flash("抄表資料已建立", "success")
        return redirect(url_for("electricity.bill_detail", bill_id=bill.id))
    return render_template("electricity/reading_form.html", form=form, bill=bill, title="新增抄表")


@electricity_bp.get("/bills/<int:bill_id>")
@login_required
def bill_detail(bill_id: int):
    bill = ElectricityBillRepository.get_or_404(bill_id)
    readings = ElectricityReadingRepository.list_for_bill(bill_id)
    return render_template("electricity/bill_detail.html", bill=bill, readings=readings)


@electricity_bp.post("/bills/<int:bill_id>/calculate")
@login_required
def bill_calculate(bill_id: int):
    bill = ElectricityBillRepository.get_or_404(bill_id)
    ElectricityService.calculate_bill(bill)
    flash("電費單已標記為 calculated", "success")
    return redirect(url_for("electricity.bill_detail", bill_id=bill.id))


@electricity_bp.route("/bills/<int:bill_id>/post", methods=["GET", "POST"])
@login_required
def bill_post(bill_id: int):
    bill = ElectricityBillRepository.get_or_404(bill_id)
    readings = ElectricityReadingRepository.list_for_bill(bill_id)
    form = ElectricityPostForm()
    form.reading_id.choices = [
        (reading.id, f"Reading {reading.id} / Room {reading.room_id or '-'} / Usage {reading.usage}") for reading in readings
    ]
    if form.validate_on_submit():
        selected = next(item for item in readings if item.id == form.reading_id.data)
        ElectricityService.post_reading_to_monthly_bill(
            monthly_bill_id=form.monthly_bill_id.data,
            reading=selected,
            public_electricity=form.public_electricity.data,
        )
        flash("電費已回寫月帳單", "success")
        return redirect(url_for("electricity.bill_detail", bill_id=bill.id))
    return render_template("electricity/post_form.html", form=form, bill=bill, title="回寫月帳單")
