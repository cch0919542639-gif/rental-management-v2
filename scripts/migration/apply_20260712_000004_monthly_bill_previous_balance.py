"""Add a separate carry-forward balance to monthly bills.

Default mode is dry-run.  The new column is additive and existing rows receive
zero, so imported historical totals are not recalculated by this migration.

Rollback: restore the target database backup. SQLite cannot safely remove the
column in place for this project.
"""

from sqlalchemy import inspect, text


MIGRATION_ID = "20260712_000004_monthly_bill_previous_balance"
DESCRIPTION = "Add previous_balance to monthly_bills for carry-forward unpaid amounts."


def run_migration(context):
    inspector = inspect(context.db.engine)
    if not inspector.has_table("monthly_bills"):
        if context.execute:
            raise RuntimeError("Base table missing: monthly_bills")
        return {"summary": "monthly_bills missing (dry-run only)"}
    columns = {column["name"] for column in inspector.get_columns("monthly_bills")}
    if "previous_balance" in columns:
        return {"summary": "monthly_bills.previous_balance already exists"}
    if not context.execute:
        return {"summary": "would add monthly_bills.previous_balance NUMERIC(10,2) NOT NULL DEFAULT 0"}

    context.db.session.execute(
        text("ALTER TABLE monthly_bills ADD COLUMN previous_balance NUMERIC(10,2) NOT NULL DEFAULT 0")
    )
    context.db.session.commit()
    return {"summary": "added monthly_bills.previous_balance with default 0"}
