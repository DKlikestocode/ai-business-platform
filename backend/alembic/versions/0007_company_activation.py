"""Add company_activation for server-owned setup state.

Revision ID: 0007_company_activation
Revises: 0006_lead_qualification
Create Date: 2026-06-13 20:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_company_activation"
down_revision: Union[str, Sequence[str], None] = "0006_lead_qualification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "company_activation",
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="awaiting_widget",
        ),
        sa.Column("install_token", sa.String(length=255), nullable=False),
        sa.Column("website_url", sa.String(length=2048), nullable=True),
        sa.Column("widget_live_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("widget_last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("widget_last_origin", sa.String(length=2048), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("company_id"),
    )


def downgrade() -> None:
    op.drop_table("company_activation")
