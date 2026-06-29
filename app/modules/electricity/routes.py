from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.modules.electricity.forms import (
    ElectricityBillForm,
    ElectricityMeterForm,
    ElectricityPostForm,
    ElectricityReadingForm,
    PropertyQuickReadingForm,
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


def _populate_property_bill_form(form: ElectricityBillForm, property_id: int):
    property_obj = PropertyRepository.get_or_404(property_id)
    meters = ElectricityMeterRepository.list_for_property(property_id)
    form.property_id.choices = [(property_obj.id, property_obj.name)]
    form.meter_id.choices = [(0, "未指定")] + [
        (meter.id, f"Meter {meter.id} / {meter.meter_number or meter.room_number or property_obj.name}") for meter in meters
    ]
    form.calc_method_id.choices = [(0, "未指定")] + [
        (item.id, item.name) for item in CalcMethodRepository.list_active()
    ]
    return property_obj


def _populate_reading_form(form: ElectricityReadingForm):
    form.meter_id.choices = [
        (meter.id, f"Meter {meter.id} / Property {meter.property_id}") for meter in ElectricityMeterRepository.list_all()
    ]
    form.room_id.choices = [(0, "未指定")] + [
        (room.id, f"{room.property.name} / {room.room_number}") for room in RoomRepository.list_all()
    ]


def _populate_property_quick_reading_form(form: PropertyQuickReadingForm, property_id: int):
    property_obj = PropertyRepository.get_or_404(property_id)
    bills = ElectricityBillRepository.list_for_property(property_id)
    meters = ElectricityMeterRepository.list_for_property(property_id)
    rooms = [room for room in RoomRepository.list_all() if room.property_id == property_id]
    form.bill_id.choices = [
        (bill.id, f"#{bill.id} / {bill.year_month} / {bill.period_start} ~ {bill.period_end}") for bill in bills
    ]
    form.meter_id.choices = [
        (meter.id, f"Meter {meter.id} / {meter.meter_number or meter.room_number or property_obj.name}") for meter in meters
    ]
    form.room_id.choices = [(0, "未指定")] + [
        (room.id, f"{room.property.name} / {room.room_number}") for room in rooms
    ]
    return property_obj, bills, meters


@electricity_bp.get("/")
@login_required
def electricity_dashboard():
    bills = ElectricityBillRepository.list_all()
    meters = ElectricityMeterRepository.list_all()
    return render_template("electricity/index.html", bills=bills, meters=meters, selected_property=None)


@electricity_bp.get("/property/<int:property_id>/bills")
@login_required
def electricity_property_bills(property_id: int):
    bills = ElectricityBillRepository.list_for_property(property_id)
    meters = ElectricityMeterRepository.list_all()
    selected_property = PropertyRepository.get_or_404(property_id)
    return render_template(
        "electricity/index.html",
        bills=bills,
        meters=meters,
        selected_property=selected_property,
    )


@electricity_bp.get("/property/<int:property_id>")
@login_required
def electricity_property_detail(property_id: int):
    property_obj = PropertyRepository.get_or_404(property_id)
    meters = ElectricityMeterRepository.list_for_property(property_id)
    bills = ElectricityBillRepository.list_for_property(property_id)
    overview = ElectricityService.property_overview(property_obj=property_obj, meters=meters, bills=bills)
    latest_bills = ElectricityBillRepository.latest_for_property(property_id, limit=10)
    return render_template(
        "electricity/property_detail.html",
        property=property_obj,
        meters=meters,
        bills=latest_bills,
        overview=overview,
    )


@electricity_bp.route("/property/<int:property_id>/new-bill", methods=["GET", "POST"])
@login_required
def electricity_property_new_bill(property_id: int):
    form = ElectricityBillForm()
    property_obj = _populate_property_bill_form(form, property_id)
    if not form.is_submitted():
        form.property_id.data = property_id
    if form.validate_on_submit():
        bill = ElectricityService.create_bill(
            property_id=property_id,
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
        flash("物件電費單已建立", "success")
        return redirect(url_for("electricity.bill_detail", bill_id=bill.id))
    return render_template(
        "electricity/bill_form.html",
        form=form,
        title=f"新增電費單：{property_obj.name}",
    )


@electricity_bp.route("/property/<int:property_id>/quick-reading", methods=["GET", "POST"])
@login_required
def electricity_property_quick_reading(property_id: int):
    form = PropertyQuickReadingForm()
    property_obj, bills, meters = _populate_property_quick_reading_form(form, property_id)
    if not bills:
        flash("此物件尚無電費單，請先建立電費單", "error")
        return redirect(url_for("electricity.electricity_property_new_bill", property_id=property_id))
    if not meters:
        flash("此物件尚無電表，請先建立電表", "error")
        return redirect(url_for("electricity.meter_create"))
    if not form.is_submitted():
        form.bill_id.data = bills[0].id
        form.meter_id.data = meters[0].id
    if form.validate_on_submit():
        bill = ElectricityBillRepository.get_or_404(form.bill_id.data)
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
        flash("物件抄表資料已建立", "success")
        return redirect(url_for("electricity.bill_detail", bill_id=bill.id))
    return render_template(
        "electricity/property_reading_form.html",
        form=form,
        property=property_obj,
        title=f"快速抄表：{property_obj.name}",
    )


@electricity_bp.get("/property/<int:property_id>/reading-log")
@login_required
def electricity_property_reading_log(property_id: int):
    property_obj = PropertyRepository.get_or_404(property_id)
    readings = ElectricityReadingRepository.list_for_property(property_id)
    return render_template("electricity/reading_log.html", property=property_obj, readings=readings)


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
