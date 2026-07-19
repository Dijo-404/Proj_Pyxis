# ruff: noqa: E501
"""Add API-backed workspace fields to persisted risk cases.

Revision ID: 20260718_0002
Revises: 20260718_0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260718_0002"
down_revision: str | None = "20260718_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("risk_cases") as batch:
        batch.add_column(
            sa.Column(
                "customer_name",
                sa.String(length=200),
                nullable=False,
                server_default="Unknown customer",
            )
        )
        batch.add_column(
            sa.Column(
                "customer_type", sa.String(length=32), nullable=False, server_default="UNKNOWN"
            )
        )
        batch.add_column(
            sa.Column(
                "business", sa.String(length=200), nullable=False, server_default="Not provided"
            )
        )
        batch.add_column(
            sa.Column(
                "trigger_transaction_id",
                sa.String(length=128),
                nullable=False,
                server_default="UNAVAILABLE",
            )
        )
        batch.add_column(
            sa.Column(
                "trigger_summary",
                sa.Text(),
                nullable=False,
                server_default="No trigger summary provided",
            )
        )
        batch.add_column(
            sa.Column("trigger_amount", sa.String(length=64), nullable=False, server_default="₹0")
        )
        batch.add_column(
            sa.Column(
                "assigned_to", sa.String(length=128), nullable=False, server_default="Unassigned"
            )
        )
        batch.add_column(
            sa.Column(
                "location", sa.String(length=200), nullable=False, server_default="Not provided"
            )
        )
        batch.add_column(
            sa.Column("workspace_data", sa.JSON(), nullable=False, server_default="{}")
        )


def downgrade() -> None:
    with op.batch_alter_table("risk_cases") as batch:
        batch.drop_column("workspace_data")
        batch.drop_column("location")
        batch.drop_column("assigned_to")
        batch.drop_column("trigger_amount")
        batch.drop_column("trigger_summary")
        batch.drop_column("trigger_transaction_id")
        batch.drop_column("business")
        batch.drop_column("customer_type")
        batch.drop_column("customer_name")
