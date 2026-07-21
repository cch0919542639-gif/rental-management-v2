"""Create the R6 move-out settlement and manual allocation ledger."""

from sqlalchemy import inspect, text

MIGRATION_ID = "20260719_000006_move_out_settlements"
DESCRIPTION = "Create independent move-out settlement and manual deposit-allocation ledger."


def run_migration(context):
    inspector = inspect(context.db.engine)
    required_tables = {"contracts", "monthly_bills", "user"}
    missing_tables = sorted(name for name in required_tables if not inspector.has_table(name))
    if missing_tables:
        message = f"Missing required base tables: {', '.join(missing_tables)}"
        if context.execute:
            raise RuntimeError(message)
        return {"summary": f"would stop: {message}"}
    if inspector.has_table("move_out_settlements"):
        return {"summary": "move_out_settlements already exists"}
    if not context.execute:
        return {"summary": "would create move_out_settlements and move_out_settlement_allocations tables"}
    context.db.session.execute(text("""
        CREATE TABLE move_out_settlements (
            id INTEGER PRIMARY KEY, contract_id INTEGER NOT NULL UNIQUE REFERENCES contracts(id) ON DELETE RESTRICT,
            final_monthly_bill_id INTEGER REFERENCES monthly_bills(id) ON DELETE RESTRICT, move_out_date DATE NOT NULL,
            final_rent NUMERIC(10,2) NOT NULL DEFAULT 0, electricity_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
            water_amount NUMERIC(10,2) NOT NULL DEFAULT 0, management_fee NUMERIC(10,2) NOT NULL DEFAULT 0,
            previous_debt NUMERIC(10,2) NOT NULL DEFAULT 0, cleaning_fee NUMERIC(10,2) NOT NULL DEFAULT 0,
            repair_fee NUMERIC(10,2) NOT NULL DEFAULT 0, other_charge NUMERIC(10,2) NOT NULL DEFAULT 0,
            other_desc VARCHAR(200), deposit_held NUMERIC(10,2) NOT NULL DEFAULT 0,
            refund_amount NUMERIC(10,2) NOT NULL DEFAULT 0, status VARCHAR(20) NOT NULL DEFAULT 'draft',
            evidence_type VARCHAR(20), evidence_reference VARCHAR(200), notes TEXT,
            created_by_id INTEGER REFERENCES user(id) ON DELETE SET NULL, settled_at DATETIME,
            voided_at DATETIME, void_reason VARCHAR(200), created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))
    context.db.session.execute(text("""
        CREATE TABLE move_out_settlement_allocations (
            id INTEGER PRIMARY KEY, settlement_id INTEGER NOT NULL REFERENCES move_out_settlements(id) ON DELETE RESTRICT,
            charge_type VARCHAR(30) NOT NULL, amount NUMERIC(10,2) NOT NULL,
            confirmed_by_id INTEGER REFERENCES user(id) ON DELETE SET NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))
    context.db.session.commit()
    return {"summary": "created R6 move-out settlement ledger tables"}
