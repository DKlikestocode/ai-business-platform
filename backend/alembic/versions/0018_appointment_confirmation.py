"""Add appointment confirmation preference and sent timestamp.

Revision ID: 0018_appointment_confirmation
Revises: 0017_customer_confirmation
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0018_appointment_confirmation"
down_revision: Union[str, Sequence[str], None] = "0017_customer_confirmation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("appointment_confirmation_preference", sa.String(16), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("appointment_confirmation_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("leads", "appointment_confirmation_sent_at")
    op.drop_column("leads", "appointment_confirmation_preference")
