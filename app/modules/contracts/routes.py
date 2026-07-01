from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.core.security import admin_required
from app.repositories import ContractRepository, RoomRepository, TenantRepository
from app.modules.contracts.forms import ContractForm
from app.services import ContractService

contracts_bp = Blueprint("contracts", __name__, url_prefix="/contracts")


def _populate_choices(form: ContractForm):
    form.tenant_id.choices = [(tenant.id, tenant.name) for tenant in TenantRepository.list_all()]
    form.room_id.choices = [
        (room.id, f"{room.property.name} / {room.room_number}") for room in RoomRepository.list_all()
    ]


@contracts_bp.get("/")
@login_required
def contract_list():
    contracts = ContractRepository.list_all()
    return render_template("contracts/list.html", contracts=contracts)


@contracts_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def contract_create():
    form = ContractForm()
    _populate_choices(form)
    if form.validate_on_submit():
        ContractService.create_contract(
            tenant_id=form.tenant_id.data,
            room_id=form.room_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            rent=form.rent.data,
            deposit=form.deposit.data,
            electricity_rate=form.electricity_rate.data,
            water_rate=form.water_rate.data,
            start_electricity_reading=form.start_electricity_reading.data,
            start_water_reading=form.start_water_reading.data,
            notes=form.notes.data,
        )
        flash("合約已建立", "success")
        return redirect(url_for("contracts.contract_list"))
    return render_template("contracts/form.html", form=form, title="新增合約")


@contracts_bp.route("/<int:contract_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def contract_edit(contract_id: int):
    contract = ContractRepository.get_or_404(contract_id)
    form = ContractForm(obj=contract)
    _populate_choices(form)
    if form.validate_on_submit():
        ContractService.update_contract(
            contract,
            tenant_id=form.tenant_id.data,
            room_id=form.room_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            rent=form.rent.data,
            deposit=form.deposit.data,
            electricity_rate=form.electricity_rate.data,
            water_rate=form.water_rate.data,
            start_electricity_reading=form.start_electricity_reading.data,
            start_water_reading=form.start_water_reading.data,
            notes=form.notes.data,
        )
        flash("合約已更新", "success")
        return redirect(url_for("contracts.contract_list"))
    return render_template("contracts/form.html", form=form, title="編輯合約")


@contracts_bp.post("/<int:contract_id>/terminate")
@login_required
@admin_required
def contract_terminate(contract_id: int):
    contract = ContractRepository.get_or_404(contract_id)
    ContractService.terminate_contract(contract)
    flash("合約已終止", "success")
    return redirect(url_for("contracts.contract_list"))
