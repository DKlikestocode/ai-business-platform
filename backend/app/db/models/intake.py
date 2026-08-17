import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.services.intake.models import IntakeChannel, IntakeStatus

if TYPE_CHECKING:
    from app.db.models.company import Company


class IntakeItem(Base):
    __tablename__ = "intake_items"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "channel",
            "external_id",
            name="uq_intake_items_company_channel_external_id",
        ),
        UniqueConstraint(
            "company_id",
            "channel",
            "source_sha256",
            name="uq_intake_items_company_channel_source_sha256",
        ),
        UniqueConstraint(
            "company_id",
            "channel",
            "provider_event_id",
            name="uq_intake_items_company_channel_provider_event_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=IntakeChannel.EMAIL.value,
    )
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=IntakeStatus.RECEIVED.value,
        index=True,
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    source_storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    service_address: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    service_requested: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(32), nullable=True)
    preferred_time: Mapped[str | None] = mapped_column(String(500), nullable=True)
    inquiry_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    inquiry_scope: Mapped[str | None] = mapped_column(String(32), nullable=True)
    contactable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    needs_human_review: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    review_reasons: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    recommended_action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    field_confidence: Mapped[dict[str, float]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    safety_warning: Mapped[str | None] = mapped_column(Text, nullable=True)
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("intake_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    extraction_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    exported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    extracted_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    company: Mapped["Company"] = relationship("Company", back_populates="intake_items")
    attachments: Mapped[list["IntakeAttachment"]] = relationship(
        "IntakeAttachment",
        back_populates="intake_item",
        cascade="all, delete-orphan",
        order_by="IntakeAttachment.created_at",
    )
    document: Mapped["IntakeDocument | None"] = relationship(
        "IntakeDocument",
        back_populates="intake_item",
        cascade="all, delete-orphan",
        uselist=False,
    )
    duplicate_of: Mapped["IntakeItem | None"] = relationship(
        "IntakeItem",
        remote_side="IntakeItem.id",
    )


class IntakeAttachment(Base):
    __tablename__ = "intake_attachments"
    __table_args__ = (
        UniqueConstraint(
            "intake_item_id",
            "filename",
            "sha256",
            name="uq_intake_attachments_item_filename_sha256",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intake_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("intake_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    intake_item: Mapped["IntakeItem"] = relationship(
        "IntakeItem",
        back_populates="attachments",
    )


class IntakeDocument(Base):
    __tablename__ = "intake_documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intake_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("intake_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    content_type: Mapped[str] = mapped_column(
        String(255), nullable=False, default="message/rfc822"
    )
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    intake_item: Mapped["IntakeItem"] = relationship(
        "IntakeItem",
        back_populates="document",
    )
