from app.core.db import db
from app.core.errors import ConflictError, DomainValidationError
from app.models import Tenant
from sqlalchemy.exc import IntegrityError

FORBIDDEN_TENANT_NAMES = {"空房", "待修", "待補", "倉庫", "鐵皮"}


class TenantService:
    @staticmethod
    def _validate_name(name: str):
        normalized = (name or "").strip()
        if not normalized:
            raise DomainValidationError("房客姓名不可為空")
        if normalized in FORBIDDEN_TENANT_NAMES:
            raise DomainValidationError("不可建立虛擬 tenant 名稱")
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
    def delete_tenant(tenant: Tenant):
        try:
            db.session.delete(tenant)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise ConflictError("此房客仍有關聯資料，無法刪除") from exc
