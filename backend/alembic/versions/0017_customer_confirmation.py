"""Add customer confirmation tracking and chat contact settings.

Revision ID: 0017_customer_confirmation
Revises: 0016_lead_inquiry_kind
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0017_customer_confirmation"
down_revision: Union[str, Sequence[str], None] = "0016_lead_inquiry_kind"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column(
            "send_customer_confirmation",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.add_column(
        "companies",
        sa.Column(
            "chat_share_phone",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "companies",
        sa.Column(
            "chat_share_email",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "leads",
        sa.Column("customer_confirmation_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("leads", "customer_confirmation_sent_at")
    op.drop_column("companies", "chat_share_email")
    op.drop_column("companies", "chat_share_phone")
    op.drop_column("companies", "send_customer_confirmation")
