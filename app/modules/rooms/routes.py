from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.repositories import PropertyRepository, RoomRepository
from app.modules.rooms.forms import RoomForm
from app.services import RoomService

rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")


def _populate_property_choices(form: RoomForm):
    form.property_id.choices = [(prop.id, prop.name) for prop in PropertyRepository.list_all()]


@rooms_bp.get("/")
@login_required
def room_list():
    rooms = RoomRepository.list_all()
    return render_template("rooms/list.html", rooms=rooms)


@rooms_bp.route("/create", methods=["GET", "POST"])
@login_required
def room_create():
    form = RoomForm()
    _populate_property_choices(form)
    if form.validate_on_submit():
        RoomService.create_room(
            property_id=form.property_id.data,
            room_number=form.room_number.data.strip(),
            rent=form.rent.data,
            deposit=form.deposit.data,
            area_ping=form.area_ping.data,
            status=form.status.data,
            notes=form.notes.data,
        )
        flash("房間已建立", "success")
        return redirect(url_for("rooms.room_list"))
    return render_template("rooms/form.html", form=form, title="新增房間")


@rooms_bp.route("/<int:room_id>/edit", methods=["GET", "POST"])
@login_required
def room_edit(room_id: int):
    room = RoomRepository.get_or_404(room_id)
    form = RoomForm(obj=room)
    _populate_property_choices(form)
    if form.validate_on_submit():
        RoomService.update_room(
            room,
            property_id=form.property_id.data,
            room_number=form.room_number.data.strip(),
            rent=form.rent.data,
            deposit=form.deposit.data,
            area_ping=form.area_ping.data,
            status=form.status.data,
            notes=form.notes.data,
        )
        flash("房間已更新", "success")
        return redirect(url_for("rooms.room_list"))
    return render_template("rooms/form.html", form=form, title="編輯房間")
