"""Add contacted_at timestamp to leads.

Revision ID: 0009_lead_contacted_at
Revises: 0008_first_website_inquiry
Create Date: 2026-06-21 19:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_lead_contacted_at"
down_revision: Union[str, Sequence[str], None] = "0008_first_website_inquiry"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("contacted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("leads", "contacted_at")
