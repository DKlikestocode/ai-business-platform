"""Add first website inquiry milestone to company_activation.

Revision ID: 0008_first_website_inquiry
Revises: 0007_company_activation
Create Date: 2026-06-21 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_first_website_inquiry"
down_revision: Union[str, Sequence[str], None] = "0007_company_activation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "company_activation",
        sa.Column("first_website_inquiry_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "company_activation",
        sa.Column("first_website_inquiry_lead_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_company_activation_first_website_inquiry_lead_id",
        "company_activation",
        "leads",
        ["first_website_inquiry_lead_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_company_activation_first_website_inquiry_lead_id",
        "company_activation",
        type_="foreignkey",
    )
    op.drop_column("company_activation", "first_website_inquiry_lead_id")
    op.drop_column("company_activation", "first_website_inquiry_at")
