from app.models import Tenant


class TenantRepository:
    @staticmethod
    def list_all():
        return Tenant.query.order_by(Tenant.name.asc()).all()

    @staticmethod
    def get_or_404(tenant_id: int):
        return Tenant.query.get_or_404(tenant_id)
