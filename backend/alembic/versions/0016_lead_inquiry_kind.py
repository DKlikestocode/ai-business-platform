"""Add inquiry_kind to leads for inbox categorization.

Revision ID: 0016_lead_inquiry_kind
Revises: 0015_company_trade
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0016_lead_inquiry_kind"
down_revision: Union[str, Sequence[str], None] = "0015_company_trade"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column(
            "inquiry_kind",
            sa.String(length=32),
            nullable=True,
            server_default="unknown",
        ),
    )


def downgrade() -> None:
    op.drop_column("leads", "inquiry_kind")
