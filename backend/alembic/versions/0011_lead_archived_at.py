"""Add archived_at timestamp to leads.

Revision ID: 0011_lead_archived_at
Revises: 0010_service_area_password_reset
Create Date: 2026-06-21 20:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_lead_archived_at"
down_revision: Union[str, Sequence[str], None] = "0010_service_area_password_reset"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE leads
        SET archived_at = COALESCE(contacted_at, created_at)
        WHERE status != 'new'
        """
    )


def downgrade() -> None:
    op.drop_column("leads", "archived_at")
