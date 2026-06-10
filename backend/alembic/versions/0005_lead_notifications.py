"""Add lead notification settings.

Revision ID: 0005_lead_notifications
Revises: 0004_persistent_messages
Create Date: 2026-06-10 20:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_lead_notifications"
down_revision: Union[str, Sequence[str], None] = "0004_persistent_messages"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("notification_email", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column(
            "notify_on_new_lead",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "leads",
        sa.Column("notification_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("leads", "notification_sent_at")
    op.drop_column("companies", "notify_on_new_lead")
    op.drop_column("companies", "notification_email")
