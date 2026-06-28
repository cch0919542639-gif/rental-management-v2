from app.repositories.billing_repository import BillingRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.electricity_repository import (
    CalcMethodRepository,
    ElectricityBillRepository,
    ElectricityMeterRepository,
    ElectricityReadingRepository,
)
from app.repositories.landlord_repository import LandlordRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.property_repository import PropertyRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.water_repository import WaterBillRepository

__all__ = [
    "BillingRepository",
    "CalcMethodRepository",
    "ContractRepository",
    "DashboardRepository",
    "ElectricityBillRepository",
    "ElectricityMeterRepository",
    "ElectricityReadingRepository",
    "LandlordRepository",
    "PaymentRepository",
    "PropertyRepository",
    "ReportRepository",
    "RoomRepository",
    "TenantRepository",
    "WaterBillRepository",
]
