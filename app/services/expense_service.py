from datetime import UTC, datetime
from decimal import Decimal

from app.core.db import db
from app.models.expense import PropertyExpense


class PropertyExpenseService:
    DRAFT_FIELDS = {"property_id", "transaction_date", "category", "amount", "payee", "reference_no", "notes"}

    @staticmethod
    def _assert_draft(expense):
        if expense.record_status != "draft":
            raise ValueError("Only draft expenses may be edited or deleted")

    @staticmethod
    def _validate_category(category):
        if category not in PropertyExpense.CATEGORIES:
            raise ValueError("Invalid expense category")

    @staticmethod
    def _validate_amount(amount):
        if Decimal(str(amount or 0)) <= 0:
            raise ValueError("Expense amount must be positive")

    @staticmethod
    def create(**payload):
        PropertyExpenseService._validate_category(payload["category"])
        PropertyExpenseService._validate_amount(payload["amount"])
        expense = PropertyExpense(record_status="draft", **payload)
        db.session.add(expense)
        db.session.commit()
        return expense

    @staticmethod
    def update(expense, **payload):
        PropertyExpenseService._assert_draft(expense)
        if "category" in payload:
            PropertyExpenseService._validate_category(payload["category"])
        if "amount" in payload:
            PropertyExpenseService._validate_amount(payload["amount"])
        for field, value in payload.items():
            if field in PropertyExpenseService.DRAFT_FIELDS:
                setattr(expense, field, value)
        db.session.commit()
        return expense

    @staticmethod
    def delete(expense):
        PropertyExpenseService._assert_draft(expense)
        db.session.delete(expense)
        db.session.commit()

    @staticmethod
    def transition(expense, next_status: str, *, void_reason: str | None = None):
        if next_status not in PropertyExpense.TRANSITIONS.get(expense.record_status, set()):
            raise ValueError(f"Invalid expense transition: {expense.record_status} -> {next_status}")
        if next_status == "posted" and Decimal(str(expense.amount or 0)) <= 0:
            raise ValueError("Posted expense amount must be positive")
        if next_status == "voided":
            if not (void_reason or "").strip():
                raise ValueError("Voided expense requires a reason")
            expense.void_reason = void_reason.strip()
            expense.voided_at = datetime.now(UTC).replace(tzinfo=None)
        expense.record_status = next_status
        db.session.commit()
        return expense
