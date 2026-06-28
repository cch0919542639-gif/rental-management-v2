from datetime import UTC, datetime
from decimal import Decimal

from app.core.db import db
from app.core.errors import ConflictError, DomainValidationError
from app.models import MonthlyBill, PaymentRecord, User
from app.repositories import BillingRepository, PaymentRepository
from app.services.payment_reconciliation_service import PaymentReconciliationService

VALID_PAYMENT_TRANSITIONS = {
    "pending": {"verified", "rejected"},
    "verified": {"linked"},
    "rejected": set(),
    "linked": set(),
}


class PaymentService:
    @staticmethod
    def _normalize_amount(amount):
        normalized = Decimal(str(amount or 0))
        if normalized < 0:
            raise DomainValidationError("付款金額不可為負值")
        return normalized

    @staticmethod
    def _validate_transition(record: PaymentRecord, next_status: str):
        current_status = record.record_status or "pending"
        allowed = VALID_PAYMENT_TRANSITIONS.get(current_status, set())
        if next_status not in allowed:
            raise ConflictError(f"付款狀態不可從 {current_status} 轉成 {next_status}")

    @staticmethod
    def create_payment_record(**payload):
        payload["amount"] = PaymentService._normalize_amount(payload.get("amount"))

        transaction_id = (payload.get("transaction_id") or "").strip()
        if transaction_id:
            existing = PaymentRepository.get_by_transaction_id(transaction_id)
            if existing:
                raise ConflictError("transaction_id 已存在")
            payload["transaction_id"] = transaction_id
        else:
            payload["transaction_id"] = None

        if payload.get("monthly_bill_id"):
            monthly_bill = BillingRepository.get_or_404(payload["monthly_bill_id"])
            payload["contract_id"] = payload.get("contract_id") or monthly_bill.contract_id

        record = PaymentRecord(record_status="pending", **payload)
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def verify_payment(record: PaymentRecord, *, verified_by: User | None = None, notes: str | None = None):
        PaymentService._validate_transition(record, "verified")
        record.record_status = "verified"
        record.verified_by = verified_by
        record.verified_at = datetime.now(UTC)
        if notes is not None:
            record.notes = notes
        db.session.commit()
        return record

    @staticmethod
    def reject_payment(record: PaymentRecord, *, verified_by: User | None = None, notes: str | None = None):
        PaymentService._validate_transition(record, "rejected")
        record.record_status = "rejected"
        record.verified_by = verified_by
        record.verified_at = datetime.now(UTC)
        if notes:
            record.notes = notes
        db.session.commit()
        return record

    @staticmethod
    def link_payment(record: PaymentRecord, *, monthly_bill_id: int, verified_by: User | None = None, notes: str | None = None):
        PaymentService._validate_transition(record, "linked")
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)

        if record.contract_id and record.contract_id != monthly_bill.contract_id:
            raise ConflictError("付款記錄 contract 與帳單 contract 不一致")

        record.monthly_bill_id = monthly_bill.id
        record.contract_id = monthly_bill.contract_id
        record.record_status = "linked"
        record.verified_by = verified_by
        record.verified_at = datetime.now(UTC)

        if notes is not None:
            record.notes = notes

        if PaymentReconciliationService.is_bill_paid(bill_total=monthly_bill.total, paid_amount=record.amount):
            monthly_bill.paid = True
            monthly_bill.paid_date = record.transaction_date

        db.session.commit()
        return record
