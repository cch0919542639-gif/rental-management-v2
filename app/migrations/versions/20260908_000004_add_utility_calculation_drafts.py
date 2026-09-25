"""add utility calculation drafts

Revision ID: 20260908_000004
Revises: 20260903_000003
Create Date: 2026-09-08 00:00:04
"""

from alembic import op
import sqlalchemy as sa


revision = "20260908_000004"
down_revision = "20260903_000003"
branch_labels = None
depends_on = None


def upgrade():
    existing = sa.inspect(op.get_bind()).get_table_names()
    if "utility_calculation_drafts" not in existing:
        op.create_table(
            "utility_calculation_drafts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("utility_type", sa.String(length=20), nullable=False),
            sa.Column("property_id", sa.Integer(), nullable=False),
            sa.Column("water_bill_id", sa.Integer(), nullable=True),
            sa.Column("electricity_bill_id", sa.Integer(), nullable=True),
            sa.Column("year_month", sa.String(length=6), nullable=False),
            sa.Column("billing_start", sa.Date(), nullable=False),
            sa.Column("billing_end", sa.Date(), nullable=False),
            sa.Column("policy_code", sa.String(length=50), nullable=False),
            sa.Column("rounding_mode", sa.String(length=40), nullable=False),
            sa.Column("billed_total", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
            sa.Column("allocated_total", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
            sa.Column("reconciliation_difference", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
            sa.Column("confirmed_at", sa.DateTime(), nullable=True),
            sa.Column("posted_at", sa.DateTime(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.CheckConstraint(
                "(water_bill_id IS NOT NULL AND electricity_bill_id IS NULL) "
                "OR (water_bill_id IS NULL AND electricity_bill_id IS NOT NULL)",
                name="ck_utility_draft_has_exactly_one_source_bill",
            ),
            sa.ForeignKeyConstraint(["property_id"], ["properties.id"]),
            sa.ForeignKeyConstraint(["water_bill_id"], ["water_bills.id"]),
            sa.ForeignKeyConstraint(["electricity_bill_id"], ["electricity_bills.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_utility_calculation_drafts_property_id", "utility_calculation_drafts", ["property_id"])
        op.create_index("ix_utility_calculation_drafts_status", "utility_calculation_drafts", ["status"])
        op.create_index("ix_utility_calculation_drafts_utility_type", "utility_calculation_drafts", ["utility_type"])
        op.create_index("ix_utility_calculation_drafts_year_month", "utility_calculation_drafts", ["year_month"])

    if "utility_calculation_lines" not in existing:
        op.create_table(
            "utility_calculation_lines",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("draft_id", sa.Integer(), nullable=False),
            sa.Column("room_id", sa.Integer(), nullable=True),
            sa.Column("contract_id", sa.Integer(), nullable=True),
            sa.Column("monthly_bill_id", sa.Integer(), nullable=True),
            sa.Column("room_number_snapshot", sa.String(length=20), nullable=False),
            sa.Column("occupant_name_snapshot", sa.String(length=100), nullable=True),
            sa.Column("occupancy_status", sa.String(length=20), nullable=False),
            sa.Column("exclusion_reason", sa.String(length=200), nullable=True),
            sa.Column("stay_days", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("calculated_amount", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
            sa.Column("confirmed_amount", sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["draft_id"], ["utility_calculation_drafts.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
            sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
            sa.ForeignKeyConstraint(["monthly_bill_id"], ["monthly_bills.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_utility_calculation_lines_draft_id", "utility_calculation_lines", ["draft_id"])
        op.create_index("ix_utility_calculation_lines_room_id", "utility_calculation_lines", ["room_id"])
        op.create_index("ix_utility_calculation_lines_contract_id", "utility_calculation_lines", ["contract_id"])
        op.create_index("ix_utility_calculation_lines_monthly_bill_id", "utility_calculation_lines", ["monthly_bill_id"])


def downgrade():
    existing = sa.inspect(op.get_bind()).get_table_names()
    if "utility_calculation_lines" in existing:
        op.drop_table("utility_calculation_lines")
    if "utility_calculation_drafts" in existing:
        op.drop_table("utility_calculation_drafts")
