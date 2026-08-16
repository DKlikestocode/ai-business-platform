"""Add channel-neutral intake items and attachments.

Revision ID: 0019_intake_items
Revises: 0018_appointment_confirmation
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0019_intake_items"
down_revision: str | Sequence[str] | None = "0018_appointment_confirmation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "intake_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("provider_event_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("sender_name", sa.String(length=255), nullable=True),
        sa.Column("sender_email", sa.String(length=320), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_sha256", sa.String(length=64), nullable=False),
        sa.Column("source_storage_key", sa.String(length=1024), nullable=True),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("customer_company", sa.String(length=255), nullable=True),
        sa.Column("customer_email", sa.String(length=320), nullable=True),
        sa.Column("customer_phone", sa.String(length=50), nullable=True),
        sa.Column(
            "service_address", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("service_requested", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("urgency", sa.String(length=32), nullable=True),
        sa.Column("preferred_time", sa.String(length=500), nullable=True),
        sa.Column("inquiry_kind", sa.String(length=32), nullable=True),
        sa.Column("inquiry_scope", sa.String(length=32), nullable=True),
        sa.Column("contactable", sa.Boolean(), nullable=False),
        sa.Column("needs_human_review", sa.Boolean(), nullable=False),
        sa.Column(
            "review_reasons", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("recommended_action", sa.String(length=64), nullable=True),
        sa.Column(
            "field_confidence", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("safety_warning", sa.Text(), nullable=True),
        sa.Column("duplicate_of_id", sa.Uuid(), nullable=True),
        sa.Column("extraction_model", sa.String(length=100), nullable=True),
        sa.Column("processing_error", sa.Text(), nullable=True),
        sa.Column("processing_attempts", sa.Integer(), nullable=False),
        sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "extracted_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["duplicate_of_id"], ["intake_items.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id",
            "channel",
            "external_id",
            name="uq_intake_items_company_channel_external_id",
        ),
        sa.UniqueConstraint(
            "company_id",
            "channel",
            "source_sha256",
            name="uq_intake_items_company_channel_source_sha256",
        ),
        sa.UniqueConstraint(
            "company_id",
            "channel",
            "provider_event_id",
            name="uq_intake_items_company_channel_provider_event_id",
        ),
    )
    op.create_index("ix_intake_items_company_id", "intake_items", ["company_id"])
    op.create_index("ix_intake_items_status", "intake_items", ["status"])

    op.create_table(
        "intake_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intake_item_id", sa.Uuid(), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["intake_item_id"], ["intake_items.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("intake_item_id"),
    )
    op.create_index(
        "ix_intake_documents_intake_item_id",
        "intake_documents",
        ["intake_item_id"],
        unique=True,
    )

    op.create_table(
        "intake_attachments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intake_item_id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("storage_key", sa.String(length=1024), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["intake_item_id"], ["intake_items.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "intake_item_id",
            "filename",
            "sha256",
            name="uq_intake_attachments_item_filename_sha256",
        ),
    )
    op.create_index(
        "ix_intake_attachments_intake_item_id",
        "intake_attachments",
        ["intake_item_id"],
    )

    op.execute(
        sa.text(
            """
            INSERT INTO intake_items (
                id,
                company_id,
                channel,
                external_id,
                status,
                subject,
                sender_name,
                sender_email,
                received_at,
                source_sha256,
                customer_name,
                customer_company,
                customer_email,
                customer_phone,
                service_address,
                service_requested,
                description,
                urgency,
                preferred_time,
                inquiry_kind,
                inquiry_scope,
                contactable,
                needs_human_review,
                review_reasons,
                recommended_action,
                field_confidence,
                processing_attempts,
                processed_at,
                exported_at,
                extracted_data,
                created_at,
                updated_at
            )
            SELECT
                leads.id,
                leads.company_id,
                CASE conversations.channel
                    WHEN 'voice' THEN 'voice'
                    WHEN 'whatsapp' THEN 'whatsapp'
                    ELSE 'website'
                END,
                leads.id::text,
                CASE
                    WHEN leads.status = 'new' THEN 'needs_review'
                    ELSE 'exported'
                END,
                LEFT(
                    COALESCE(
                        NULLIF(leads.service_requested, ''),
                        NULLIF(leads.summary, ''),
                        'Kundenanfrage'
                    ),
                    500
                ),
                NULLIF(leads.name, ''),
                leads.email,
                leads.created_at,
                repeat(md5('lead:' || leads.id::text), 2),
                NULLIF(leads.name, ''),
                leads.company,
                leads.email,
                NULLIF(leads.phone, ''),
                jsonb_build_object(
                    'street', NULL,
                    'postal_code', leads.postal_code,
                    'city', NULLIF(leads.location, '')
                ),
                NULLIF(leads.service_requested, ''),
                COALESCE(NULLIF(leads.description, ''), leads.summary),
                CASE lower(leads.urgency)
                    WHEN 'hoch' THEN 'high'
                    WHEN 'high' THEN 'high'
                    WHEN 'mittel' THEN 'medium'
                    WHEN 'medium' THEN 'medium'
                    WHEN 'niedrig' THEN 'low'
                    WHEN 'low' THEN 'low'
                    ELSE 'unknown'
                END,
                NULLIF(leads.preferred_callback_time, ''),
                CASE
                    WHEN leads.inquiry_kind IN ('appointment_consultation', 'quote')
                        THEN leads.inquiry_kind
                    ELSE 'other'
                END,
                'unclear',
                leads.contactable,
                leads.status = 'new',
                CASE
                    WHEN leads.status = 'new'
                        THEN jsonb_build_array(
                            'Aus einer bestehenden digitalen Anfrage übernommen; Angaben vor Export prüfen.'
                        )
                    ELSE '[]'::jsonb
                END,
                CASE
                    WHEN NOT leads.contactable THEN 'request_missing_information'
                    WHEN lower(leads.urgency) IN ('hoch', 'high') THEN 'call_immediately'
                    WHEN leads.inquiry_kind = 'quote' THEN 'prepare_quote'
                    ELSE 'schedule_visit'
                END,
                '{}'::jsonb,
                0,
                leads.created_at,
                CASE
                    WHEN leads.status <> 'new'
                        THEN COALESCE(leads.archived_at, leads.created_at)
                    ELSE NULL
                END,
                jsonb_build_object(
                    'source', 'lead',
                    'lead_id', leads.id::text,
                    'conversation_id', leads.conversation_id,
                    'qualification_status', leads.qualification_status,
                    'lead_score', leads.lead_score
                ),
                leads.created_at,
                leads.created_at
            FROM leads
            LEFT JOIN conversations
                ON conversations.company_id = leads.company_id
                AND conversations.external_id = leads.conversation_id
            WHERE COALESCE(conversations.channel, 'web')
                NOT IN ('dashboard', 'landing_demo')
            """
        )
    )


def downgrade() -> None:
    op.drop_index(
        "ix_intake_attachments_intake_item_id", table_name="intake_attachments"
    )
    op.drop_table("intake_attachments")
    op.drop_index(
        "ix_intake_documents_intake_item_id", table_name="intake_documents"
    )
    op.drop_table("intake_documents")
    op.drop_index("ix_intake_items_status", table_name="intake_items")
    op.drop_index("ix_intake_items_company_id", table_name="intake_items")
    op.drop_table("intake_items")
