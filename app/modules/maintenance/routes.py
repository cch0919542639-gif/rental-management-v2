from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.modules.maintenance.forms import MaintenanceFilterForm, MaintenanceRequestForm
from app.repositories import MaintenanceRepository, RoomRepository
from app.services import MaintenanceService

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/maintenance")


def _populate_room_choices(form: MaintenanceRequestForm):
    form.room_id.choices = [
        (room.id, f"{room.property.name} / {room.room_number}") for room in RoomRepository.list_all()
    ]


def _build_filters(args):
    room_id = args.get("room_id", type=int)
    return {
        "status": (args.get("status") or "").strip() or None,
        "priority": (args.get("priority") or "").strip() or None,
        "room_id": room_id or None,
        "reported_from": args.get("reported_from", type=str) or None,
        "reported_to": args.get("reported_to", type=str) or None,
    }


def _populate_filter_choices(form: MaintenanceFilterForm):
    form.room_id.choices = [(0, "全部")] + [
        (room.id, f"{room.property.name} / {room.room_number}") for room in RoomRepository.list_all()
    ]


def _init_filter_form():
    form = MaintenanceFilterForm(request.args, meta={"csrf": False})
    _populate_filter_choices(form)
    return form


@maintenance_bp.get("/")
@login_required
def maintenance_index():
    filters = _build_filters(request.args)
    filter_form = _init_filter_form()
    rooms = MaintenanceService.room_snapshot()
    requests = MaintenanceService.list_filtered_requests(**filters)
    summary = MaintenanceService.summary(**filters)
    return render_template(
        "maintenance/index.html",
        rooms=rooms,
        requests=requests,
        filter_form=filter_form,
        summary=summary,
        scope_label="全部維修單",
    )


@maintenance_bp.get("/open")
@login_required
def maintenance_open():
    filters = _build_filters(request.args)
    filter_form = _init_filter_form()
    rooms = MaintenanceService.room_snapshot()
    requests = MaintenanceService.list_open_requests(**filters)
    summary = MaintenanceService.summary(**filters)
    return render_template(
        "maintenance/index.html",
        rooms=rooms,
        requests=requests,
        filter_form=filter_form,
        summary=summary,
        scope_label="Open 維修單",
    )


@maintenance_bp.get("/rooms/<int:room_id>")
@login_required
def maintenance_room_requests(room_id: int):
    room = RoomRepository.get_or_404(room_id)
    filters = _build_filters(request.args)
    filters["room_id"] = room_id
    filter_form = _init_filter_form()
    filter_form.room_id.data = room_id
    rooms = MaintenanceService.room_snapshot()
    requests = MaintenanceService.list_filtered_requests(**filters)
    summary = MaintenanceService.summary(**filters)
    return render_template(
        "maintenance/index.html",
        rooms=rooms,
        requests=requests,
        filter_form=filter_form,
        summary=summary,
        scope_label=f"房間維修單：{room.property.name} / {room.room_number}",
    )


@maintenance_bp.route("/create", methods=["GET", "POST"])
@login_required
def maintenance_create():
    form = MaintenanceRequestForm()
    _populate_room_choices(form)
    if form.validate_on_submit():
        MaintenanceService.create_request(
            room_id=form.room_id.data,
            issue_category=form.issue_category.data,
            priority=form.priority.data,
            title=form.title.data.strip(),
            description=form.description.data,
            reported_by_name=form.reported_by_name.data,
            assigned_to_name=form.assigned_to_name.data,
            estimated_cost=form.estimated_cost.data,
            actual_cost=form.actual_cost.data,
            notes=form.notes.data,
        )
        flash("維修單已建立", "success")
        return redirect(url_for("maintenance.maintenance_index"))
    return render_template("maintenance/form.html", form=form, title="新增維修單")


@maintenance_bp.route("/<int:request_id>/edit", methods=["GET", "POST"])
@login_required
def maintenance_edit(request_id: int):
    request_obj = MaintenanceRepository.get_or_404(request_id)
    form = MaintenanceRequestForm(obj=request_obj)
    _populate_room_choices(form)
    if form.validate_on_submit():
        MaintenanceService.update_request(
            request_obj,
            room_id=form.room_id.data,
            issue_category=form.issue_category.data,
            priority=form.priority.data,
            title=form.title.data.strip(),
            description=form.description.data,
            reported_by_name=form.reported_by_name.data,
            assigned_to_name=form.assigned_to_name.data,
            estimated_cost=form.estimated_cost.data,
            actual_cost=form.actual_cost.data,
            notes=form.notes.data,
        )
        flash("維修單已更新", "success")
        return redirect(url_for("maintenance.maintenance_index"))
    return render_template("maintenance/form.html", form=form, title="編輯維修單")


@maintenance_bp.post("/<int:request_id>/transition/<string:next_status>")
@login_required
def maintenance_transition(request_id: int, next_status: str):
    request_obj = MaintenanceRepository.get_or_404(request_id)
    try:
        MaintenanceService.transition_status(request_obj, next_status)
        flash("維修單狀態已更新", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("maintenance.maintenance_index"))
