from datetime import date

from flask import Blueprint, abort, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.modules.move_out_settlements.forms import MoveOutSettlementForm, SettlementAllocationForm
from app.models import Property
from app.repositories import ContractRepository, MoveOutSettlementRepository, PropertyRepository
from app.services import MoveOutSettlementService, ReportExportService

move_out_settlements_bp = Blueprint("move_out_settlements", __name__, url_prefix="/move-out-settlements")


def _populate_contract_choices(form):
    form.contract_id.choices = [
        (contract.id, f"#{contract.id} {contract.tenant.name}／{contract.room.property.name} {contract.room.room_number}")
        for contract in ContractRepository.list_all()
        if not contract.move_out_settlement and contract.room.property_id in _visible_property_ids()
    ]


def _payload(form):
    fields = MoveOutSettlementService.DRAFT_FIELDS - {"final_monthly_bill_id"}
    return {field: getattr(form, field).data for field in fields}


def _visible_property_ids():
    if current_user.role == "admin":
        return {item.id for item in PropertyRepository.list_all()}
    if current_user.landlord_id:
        return {item.id for item in Property.query.filter_by(landlord_id=current_user.landlord_id).all()}
    return set()


def _assert_visible(settlement):
    if settlement.contract.room.property_id not in _visible_property_ids():
        abort(403)
    return settlement


def _filter_values():
    property_id = request.args.get("property_id", type=int)
    visible_property_ids = _visible_property_ids()
    if property_id and property_id not in visible_property_ids:
        abort(403)
    try:
        move_out_from = date.fromisoformat(request.args["move_out_from"]) if request.args.get("move_out_from") else None
        move_out_to = date.fromisoformat(request.args["move_out_to"]) if request.args.get("move_out_to") else None
    except ValueError:
        abort(400)
    return {
        "status": request.args.get("status") or None,
        "property_id": property_id,
        "property_ids": [property_id] if property_id else sorted(visible_property_ids),
        "move_out_from": move_out_from,
        "move_out_to": move_out_to,
        "visible_properties": [item for item in PropertyRepository.list_all() if item.id in visible_property_ids],
    }


def _export_rows(settlements):
    return [
        {
            "move_out_date": str(item.move_out_date),
            "property_name": item.contract.room.property.name,
            "room_number": item.contract.room.room_number,
            "tenant_name": item.contract.tenant.name,
            "status": item.status,
            "gross_charges": int(item.gross_charges),
            "full_refund_amount": int(item.refund_amount or 0),
            "allocated_amount": int(item.allocated_amount),
            "net_refund_amount": int(item.net_refund_amount),
            "outstanding_amount": int(item.outstanding_amount),
            "evidence_type": item.evidence_type or "",
            "evidence_reference": item.evidence_reference or "",
        }
        for item in settlements
    ]


@move_out_settlements_bp.get("/")
@login_required
def settlement_list():
    filters = _filter_values()
    return render_template(
        "move_out_settlements/list.html",
        settlements=MoveOutSettlementRepository.list_filtered(
            status=filters["status"], property_ids=filters["property_ids"],
            move_out_from=filters["move_out_from"], move_out_to=filters["move_out_to"],
        ),
        selected_status=filters["status"], selected_property_id=filters["property_id"],
        move_out_from=filters["move_out_from"], move_out_to=filters["move_out_to"],
        properties=filters["visible_properties"],
    )


@move_out_settlements_bp.get("/export")
@login_required
def settlement_export():
    filters = _filter_values()
    settlements = MoveOutSettlementRepository.list_filtered(
        status=filters["status"], property_ids=filters["property_ids"],
        move_out_from=filters["move_out_from"], move_out_to=filters["move_out_to"],
    )
    rows = _export_rows(settlements)
    headers = [
        "move_out_date", "property_name", "room_number", "tenant_name", "status", "gross_charges",
        "full_refund_amount", "allocated_amount", "net_refund_amount", "outstanding_amount",
        "evidence_type", "evidence_reference",
    ]
    payload = ReportExportService.export_rows(
        rows=rows, headers=headers, filename_base="move-out-settlements", export_format=request.args.get("format") or "csv",
    )
    response = make_response(payload.content)
    response.headers["Content-Type"] = payload.content_type
    response.headers["Content-Disposition"] = f'attachment; filename="{payload.filename}"'
    return response


@move_out_settlements_bp.route("/create", methods=["GET", "POST"])
@login_required
def settlement_create():
    form = MoveOutSettlementForm()
    _populate_contract_choices(form)
    if form.validate_on_submit():
        try:
            contract = ContractRepository.get_or_404(form.contract_id.data)
            if contract.room.property_id not in _visible_property_ids():
                abort(403)
            settlement = MoveOutSettlementService.create(contract=contract, created_by_id=current_user.id, **_payload(form))
            flash("退租結清草稿已建立", "success")
            return redirect(url_for("move_out_settlements.settlement_detail", settlement_id=settlement.id))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("move_out_settlements/form.html", form=form, title="新增退租結清草稿")


@move_out_settlements_bp.route("/<int:settlement_id>/edit", methods=["GET", "POST"])
@login_required
def settlement_edit(settlement_id):
    settlement = _assert_visible(MoveOutSettlementRepository.get_or_404(settlement_id))
    form = MoveOutSettlementForm(obj=settlement)
    form.contract_id.choices = [(settlement.contract_id, f"#{settlement.contract_id} {settlement.contract.tenant.name}")]
    if form.validate_on_submit():
        try:
            MoveOutSettlementService.update(settlement, **_payload(form))
            flash("退租結清草稿已更新", "success")
            return redirect(url_for("move_out_settlements.settlement_detail", settlement_id=settlement.id))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("move_out_settlements/form.html", form=form, title="編輯退租結清草稿")


@move_out_settlements_bp.get("/<int:settlement_id>")
@login_required
def settlement_detail(settlement_id):
    settlement = _assert_visible(MoveOutSettlementRepository.get_or_404(settlement_id))
    allocation_form = SettlementAllocationForm()
    return render_template("move_out_settlements/detail.html", settlement=settlement, allocation_form=allocation_form)


@move_out_settlements_bp.route("/<int:settlement_id>/settle", methods=["GET", "POST"])
@login_required
def settlement_settle(settlement_id):
    settlement = _assert_visible(MoveOutSettlementRepository.get_or_404(settlement_id))
    form = SettlementAllocationForm()
    if request.method == "GET":
        for field in settlement.CHARGE_FIELDS:
            getattr(form, field).data = getattr(settlement, field)
    if form.validate_on_submit():
        try:
            MoveOutSettlementService.settle(
                settlement,
                allocations={field: getattr(form, field).data for field in settlement.CHARGE_FIELDS},
                confirmed_by=current_user,
            )
            flash("費用明細與退款分攤已由人工確認；付款與退款仍待另行認列", "success")
            return redirect(url_for("move_out_settlements.settlement_detail", settlement_id=settlement.id))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("move_out_settlements/settle.html", settlement=settlement, form=form)


@move_out_settlements_bp.post("/<int:settlement_id>/void")
@login_required
def settlement_void(settlement_id):
    settlement = _assert_visible(MoveOutSettlementRepository.get_or_404(settlement_id))
    try:
        MoveOutSettlementService.void(settlement, reason=request.form.get("void_reason") or "")
        flash("退租結清單已作廢", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("move_out_settlements.settlement_detail", settlement_id=settlement.id))


@move_out_settlements_bp.post("/<int:settlement_id>/delete")
@login_required
def settlement_delete(settlement_id):
    settlement = _assert_visible(MoveOutSettlementRepository.get_or_404(settlement_id))
    try:
        MoveOutSettlementService.delete(settlement)
        flash("退租結清草稿已刪除", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("move_out_settlements.settlement_detail", settlement_id=settlement.id))
    return redirect(url_for("move_out_settlements.settlement_list"))
