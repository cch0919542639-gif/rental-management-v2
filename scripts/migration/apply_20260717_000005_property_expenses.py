"""Create the independent PropertyExpense ledger table."""

from sqlalchemy import inspect, text

MIGRATION_ID = "20260717_000005_property_expenses"
DESCRIPTION = "Create independent property_expenses operating-expense ledger."


def run_migration(context):
    inspector = inspect(context.db.engine)
    required_tables = {"properties", "user"}
    missing_tables = sorted(name for name in required_tables if not inspector.has_table(name))
    if missing_tables:
        message = f"Missing required base tables: {', '.join(missing_tables)}"
        if context.execute:
            raise RuntimeError(message)
        return {"summary": f"would stop: {message}"}
    if inspector.has_table("property_expenses"):
        return {"summary": "property_expenses already exists"}
    if not context.execute:
        return {"summary": "would create property_expenses ledger table"}
    context.db.session.execute(text("""
        CREATE TABLE property_expenses (
            id INTEGER PRIMARY KEY, property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE RESTRICT,
            transaction_date DATE NOT NULL, category VARCHAR(30) NOT NULL, amount NUMERIC(10,2) NOT NULL,
            payee VARCHAR(100), reference_no VARCHAR(100), notes TEXT, record_status VARCHAR(20) NOT NULL DEFAULT 'draft',
            created_by_id INTEGER REFERENCES user(id) ON DELETE SET NULL, voided_at DATETIME, void_reason VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))
    context.db.session.commit()
    return {"summary": "created property_expenses ledger table"}
