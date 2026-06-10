"""Add lead qualification and contactable notification settings.

Revision ID: 0006_lead_qualification
Revises: 0005_lead_notifications
Create Date: 2026-06-10 22:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_lead_qualification"
down_revision: Union[str, Sequence[str], None] = "0005_lead_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column(
            "notify_on_contactable_lead",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "companies",
        sa.Column(
            "contactable_lead_notification_threshold",
            sa.Integer(),
            nullable=False,
            server_default="50",
        ),
    )

    op.add_column(
        "leads",
        sa.Column("contactable", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("leads", sa.Column("contact_method", sa.String(length=50), nullable=True))
    op.add_column(
        "leads",
        sa.Column("lead_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "leads",
        sa.Column(
            "qualification_status",
            sa.String(length=50),
            nullable=False,
            server_default="incomplete",
        ),
    )


def downgrade() -> None:
    op.drop_column("leads", "qualification_status")
    op.drop_column("leads", "lead_score")
    op.drop_column("leads", "contact_method")
    op.drop_column("leads", "contactable")
    op.drop_column("companies", "contactable_lead_notification_threshold")
    op.drop_column("companies", "notify_on_contactable_lead")
