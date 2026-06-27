"""Add trade to companies for industry-specific copy and prompts.

Revision ID: 0015_company_trade
Revises: 0014_notification_min_urgency
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015_company_trade"
down_revision: Union[str, Sequence[str], None] = "0014_notification_min_urgency"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("trade", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("companies", "trade")
