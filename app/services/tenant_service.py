from flask import flash

from app.core.db import db
from app.core.errors import DomainValidationError
from app.models import Tenant
from app.repositories import TenantRepository

FORBIDDEN_TENANT_NAMES = {"空房", "待修", "待补", "仓库", "铁皮"}


class TenantService:
    @staticmethod
    def _validate_name(name: str):
        normalized = (name or "").strip()
        if not normalized:
            raise DomainValidationError("房客姓名不可为空")
        if normalized in FORBIDDEN_TENANT_NAMES:
            raise DomainValidationError("不可建立虚拟 tenant 名称")
        return normalized

    @staticmethod
    def create_tenant(**payload):
        payload["name"] = TenantService._validate_name(payload["name"])
        tenant = Tenant(**payload)
        db.session.add(tenant)
        db.session.commit()
        return tenant

    @staticmethod
    def update_tenant(tenant: Tenant, **payload):
        payload["name"] = TenantService._validate_name(payload["name"])
        for key, value in payload.items():
            setattr(tenant, key, value)
        db.session.commit()
        return tenant

    @staticmethod
    def delete_tenant(tenant_id: int):
        tenant = TenantRepository.get_or_404(tenant_id)
        if tenant.contracts:
            flash(f"房客「{tenant.name}」尚有 {len(tenant.contracts)} 笔合约，无法删除", "error")
            return None
        TenantRepository.delete(tenant)
        flash("房客已删除", "success")
        return tenant
