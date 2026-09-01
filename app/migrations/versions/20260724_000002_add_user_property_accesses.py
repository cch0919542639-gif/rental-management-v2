"""add user property access grants

Revision ID: 20260724_000002
Revises: 20260701_000001
Create Date: 2026-07-24 00:00:02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260724_000002"
down_revision = "20260701_000001"
branch_labels = None
depends_on = None


def upgrade():
    if "user_property_accesses" in sa.inspect(op.get_bind()).get_table_names():
        return

    op.create_table(
        "user_property_accesses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "property_id", name="uq_user_property_access"),
    )


def downgrade():
    if "user_property_accesses" in sa.inspect(op.get_bind()).get_table_names():
        op.drop_table("user_property_accesses")
