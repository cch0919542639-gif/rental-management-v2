from app.models import Tenant
from app.repositories._helpers import session_get_or_404


class TenantRepository:
    @staticmethod
    def list_all():
        return Tenant.query.order_by(Tenant.name.asc()).all()

    @staticmethod
    def get_or_404(tenant_id: int):
        return session_get_or_404(Tenant, tenant_id)

    @staticmethod
    def delete(tenant: Tenant):
        tenant.delete()
