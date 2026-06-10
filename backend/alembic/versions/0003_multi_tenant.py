"""Add multi-tenant foundation.

Revision ID: 0003_multi_tenant
Revises: 0002_add_leads_table
Create Date: 2026-06-10 16:00:00.000000

"""

from typing import Sequence, Union

import uuid

import sqlalchemy as sa
from alembic import op

revision: str = "0003_multi_tenant"
down_revision: Union[str, Sequence[str], None] = "0002_add_leads_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_COMPANY_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_companies_slug"), "companies", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_company_id"), "users", ["company_id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id",
            "external_id",
            name="uq_conversations_company_external_id",
        ),
    )
    op.create_index(
        op.f("ix_conversations_company_id"),
        "conversations",
        ["company_id"],
        unique=False,
    )

    op.create_table(
        "agents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("agent_type", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id",
            "agent_type",
            name="uq_agents_company_agent_type",
        ),
    )
    op.create_index(op.f("ix_agents_company_id"), "agents", ["company_id"], unique=False)

    op.execute(
        sa.text(
            """
            INSERT INTO companies (id, name, slug, email, phone)
            VALUES (:id, 'Default Company', 'default', 'default@local', NULL)
            """
        ).bindparams(id=DEFAULT_COMPANY_ID),
    )

    op.add_column("leads", sa.Column("company_id", sa.Uuid(), nullable=True))
    op.execute(
        sa.text("UPDATE leads SET company_id = :company_id").bindparams(
            company_id=DEFAULT_COMPANY_ID,
        ),
    )
    op.alter_column("leads", "company_id", nullable=False)
    op.create_foreign_key(
        "fk_leads_company_id_companies",
        "leads",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_leads_company_id"), "leads", ["company_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_leads_company_id"), table_name="leads")
    op.drop_constraint("fk_leads_company_id_companies", "leads", type_="foreignkey")
    op.drop_column("leads", "company_id")

    op.drop_index(op.f("ix_agents_company_id"), table_name="agents")
    op.drop_table("agents")

    op.drop_index(op.f("ix_conversations_company_id"), table_name="conversations")
    op.drop_table("conversations")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_company_id"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_companies_slug"), table_name="companies")
    op.drop_table("companies")
