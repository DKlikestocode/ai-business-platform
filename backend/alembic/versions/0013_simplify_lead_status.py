"""Simplify lead status to new and contacted.

Revision ID: 0013_simplify_lead_status
Revises: 0012_service_area_coordinates
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0013_simplify_lead_status"
down_revision: Union[str, Sequence[str], None] = "0012_service_area_coordinates"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE leads SET status = 'contacted' WHERE status NOT IN ('new', 'contacted')"
    )


def downgrade() -> None:
    pass
