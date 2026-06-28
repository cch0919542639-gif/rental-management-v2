from calendar import monthrange
from datetime import date

from app.core.db import db
from app.core.errors import ConflictError, DomainValidationError
from app.core.year_month import to_db_year_month
from app.models import Contract, MonthlyBill
from app.repositories import BillingRepository, ContractRepository
from app.services.billing_service import BillingService


class BillingGenerationService:
    @staticmethod
    def _parse_year_month(year_month: str) -> tuple[str, date, date]:
        db_year_month = to_db_year_month(year_month)
        year = int(db_year_month[:4])
        month = int(db_year_month[4:])
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        return db_year_month, first_day, last_day

    @staticmethod
    def _contract_effective_for_month(contract: Contract, first_day: date, last_day: date) -> bool:
        if contract.status == "terminated":
            return False
        return contract.start_date <= last_day and contract.end_date >= first_day

    @staticmethod
    def _default_payload(contract: Contract, db_year_month: str):
        return {
            "contract_id": contract.id,
            "year_month": db_year_month,
            "rent": contract.rent,
            "electricity_prev": 0,
            "electricity_curr": 0,
            "electricity_usage": 0,
            "electricity_amount": 0,
            "public_electricity": 0,
            "water_prev": 0,
            "water_curr": 0,
            "water_usage": 0,
            "water_amount": 0,
            "other_charges": 0,
            "other_desc": None,
            "paid": False,
            "notes": None,
        }

    @staticmethod
    def create_monthly_bill(**payload):
        db_year_month = to_db_year_month(payload["year_month"])
        existing = BillingRepository.find_by_contract_and_month(payload["contract_id"], db_year_month)
        if existing:
            raise ConflictError("此合約在該月份已有帳單")

        contract = ContractRepository.get_or_404(payload["contract_id"])
        bill = MonthlyBill(**payload)
        bill.year_month = db_year_month
        if not bill.rent:
            bill.rent = contract.rent
        BillingService.calculate_total(bill)
        db.session.add(bill)
        db.session.commit()
        return bill

    @staticmethod
    def update_monthly_bill(bill: MonthlyBill, **payload):
        db_year_month = to_db_year_month(payload["year_month"])
        existing = BillingRepository.find_by_contract_and_month(payload["contract_id"], db_year_month)
        if existing and existing.id != bill.id:
            raise ConflictError("此合約在該月份已有另一筆帳單")

        for key, value in payload.items():
            setattr(bill, key, value)
        bill.year_month = db_year_month
        BillingService.calculate_total(bill)
        db.session.commit()
        return bill

    @staticmethod
    def toggle_paid(bill: MonthlyBill):
        bill.paid = not bill.paid
        if not bill.paid:
            bill.paid_date = None
        db.session.commit()
        return bill

    @staticmethod
    def generate_for_contract(*, contract_id: int, year_month: str, overwrite_existing: bool = False):
        db_year_month, first_day, last_day = BillingGenerationService._parse_year_month(year_month)
        contract = ContractRepository.get_or_404(contract_id)
        if not BillingGenerationService._contract_effective_for_month(contract, first_day, last_day):
            raise DomainValidationError("合約在該月份不屬於有效帳單範圍")

        existing = BillingRepository.find_by_contract_and_month(contract.id, db_year_month)
        if existing and not overwrite_existing:
            return existing, False
        if existing and overwrite_existing:
            defaults = BillingGenerationService._default_payload(contract, db_year_month)
            for key, value in defaults.items():
                setattr(existing, key, value)
            BillingService.calculate_total(existing)
            db.session.commit()
            return existing, True

        bill = MonthlyBill(**BillingGenerationService._default_payload(contract, db_year_month))
        BillingService.calculate_total(bill)
        db.session.add(bill)
        db.session.commit()
        return bill, True

    @staticmethod
    def generate_for_month(*, year_month: str, overwrite_existing: bool = False):
        db_year_month, first_day, last_day = BillingGenerationService._parse_year_month(year_month)
        created_or_updated = []
        skipped = []

        for contract in ContractRepository.list_all():
            if not BillingGenerationService._contract_effective_for_month(contract, first_day, last_day):
                continue
            existing = BillingRepository.find_by_contract_and_month(contract.id, db_year_month)
            if existing and not overwrite_existing:
                skipped.append(existing.id)
                continue
            bill, changed = BillingGenerationService.generate_for_contract(
                contract_id=contract.id,
                year_month=db_year_month,
                overwrite_existing=overwrite_existing,
            )
            if changed:
                created_or_updated.append(bill.id)

        return {
            "year_month": db_year_month,
            "created_or_updated_ids": created_or_updated,
            "skipped_ids": skipped,
        }
