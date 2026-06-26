"""service area coordinates and lead service area status

Revision ID: 0012_service_area_coordinates
Revises: 0011_lead_archived_at
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012_service_area_coordinates"
down_revision: Union[str, Sequence[str], None] = "0011_lead_archived_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("service_area_latitude", sa.Float(), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("service_area_longitude", sa.Float(), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("postal_code", sa.String(length=10), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("service_area_status", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("service_area_distance_km", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("leads", "service_area_distance_km")
    op.drop_column("leads", "service_area_status")
    op.drop_column("leads", "postal_code")
    op.drop_column("companies", "service_area_longitude")
    op.drop_column("companies", "service_area_latitude")
