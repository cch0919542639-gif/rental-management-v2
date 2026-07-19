from datetime import date
from decimal import Decimal

import pytest

from app.models import PropertyExpense
from app.services import PropertyExpenseService


def _expense(seeded_data):
    return PropertyExpenseService.create(
        property_id=seeded_data["property_id"],
        transaction_date=date(2026, 7, 1),
        category="repair",
        amount=Decimal("1200"),
        payee="維修商",
        reference_no="R-1",
        notes="test",
        created_by_id=seeded_data["user_id"],
    )


def test_property_expense_draft_post_void_and_immutability(app, seeded_data):
    with app.app_context():
        expense = _expense(seeded_data)
        PropertyExpenseService.update(expense, amount=Decimal("1300"))
        PropertyExpenseService.transition(expense, "posted")
        assert expense.record_status == "posted"
        with pytest.raises(ValueError):
            PropertyExpenseService.update(expense, amount=Decimal("1"))
        with pytest.raises(ValueError):
            PropertyExpenseService.delete(expense)
        with pytest.raises(ValueError):
            PropertyExpenseService.transition(expense, "voided")
        PropertyExpenseService.transition(expense, "voided", void_reason="重複收據")
        assert expense.void_reason == "重複收據"


def test_property_expense_delete_draft_and_export_only_posted(app, client, seeded_data):
    with app.app_context():
        draft = _expense(seeded_data)
        PropertyExpenseService.delete(draft)
        posted = _expense(seeded_data)
        PropertyExpenseService.transition(posted, "posted")
    with client.session_transaction() as session:
        session["_user_id"] = str(seeded_data["user_id"])
        session["_fresh"] = True
    response = client.get("/expenses/export?format=csv")
    assert response.status_code == 200
    assert b"R-1" in response.data


def test_property_expense_rejects_non_positive_amounts(app, seeded_data):
    with app.app_context():
        with pytest.raises(ValueError, match="amount must be positive"):
            PropertyExpenseService.create(
                property_id=seeded_data["property_id"],
                transaction_date=date(2026, 7, 1),
                category="repair",
                amount=Decimal("0"),
                created_by_id=seeded_data["user_id"],
            )
        expense = _expense(seeded_data)
        with pytest.raises(ValueError, match="amount must be positive"):
            PropertyExpenseService.update(expense, amount=Decimal("-1"))
