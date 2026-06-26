"""Add notification_min_urgency to companies.

Revision ID: 0014_notification_min_urgency
Revises: 0013_simplify_lead_status
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0014_notification_min_urgency"
down_revision: Union[str, Sequence[str], None] = "0013_simplify_lead_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column(
            "notification_min_urgency",
            sa.String(length=20),
            nullable=False,
            server_default="medium",
        ),
    )


def downgrade() -> None:
    op.drop_column("companies", "notification_min_urgency")
