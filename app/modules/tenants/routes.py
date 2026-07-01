from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.core.errors import ConflictError
from app.core.security import admin_required
from app.modules.tenants.forms import TenantForm
from app.repositories import TenantRepository
from app.services import TenantService

tenants_bp = Blueprint("tenants", __name__, url_prefix="/tenants")


@tenants_bp.get("/")
@login_required
def tenant_list():
    tenants = TenantRepository.list_all()
    return render_template("tenants/list.html", tenants=tenants)


@tenants_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def tenant_create():
    form = TenantForm()
    if form.validate_on_submit():
        TenantService.create_tenant(
            name=form.name.data,
            phone=form.phone.data,
            id_number=form.id_number.data,
            emergency_contact=form.emergency_contact.data,
            emergency_phone=form.emergency_phone.data,
            notes=form.notes.data,
        )
        flash("房客已建立", "success")
        return redirect(url_for("tenants.tenant_list"))
    return render_template("tenants/form.html", form=form, title="新增房客")


@tenants_bp.route("/<int:tenant_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def tenant_edit(tenant_id: int):
    tenant = TenantRepository.get_or_404(tenant_id)
    form = TenantForm(obj=tenant)
    if form.validate_on_submit():
        TenantService.update_tenant(
            tenant,
            name=form.name.data,
            phone=form.phone.data,
            id_number=form.id_number.data,
            emergency_contact=form.emergency_contact.data,
            emergency_phone=form.emergency_phone.data,
            notes=form.notes.data,
        )
        flash("房客已更新", "success")
        return redirect(url_for("tenants.tenant_list"))
    return render_template("tenants/form.html", form=form, title="編輯房客")


@tenants_bp.post("/<int:tenant_id>/delete")
@login_required
@admin_required
def tenant_delete(tenant_id: int):
    tenant = TenantRepository.get_or_404(tenant_id)
    try:
        TenantService.delete_tenant(tenant)
        flash("房客已刪除", "success")
    except ConflictError as exc:
        flash(exc.message, "error")
    return redirect(url_for("tenants.tenant_list"))
