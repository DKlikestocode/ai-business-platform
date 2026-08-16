import math
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.db.models.intake import IntakeItem
from app.services.intake.models import (
    IntakeChannel,
    IntakeKind,
    IntakeReviewDecision,
    IntakeScope,
    IntakeStatus,
    IntakeUrgency,
    RecommendedAction,
    ServiceAddress,
)


class IntakeAttachmentResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IntakeItemResponse(BaseModel):
    id: UUID
    company_id: UUID
    channel: IntakeChannel
    status: IntakeStatus
    subject: str
    sender_name: str | None
    sender_email: str | None
    received_at: datetime | None
    customer_name: str | None
    customer_company: str | None
    customer_email: str | None
    customer_phone: str | None
    service_address: ServiceAddress | None
    service_requested: str | None
    description: str | None
    urgency: IntakeUrgency | None
    preferred_time: str | None
    inquiry_kind: IntakeKind | None
    inquiry_scope: IntakeScope | None
    contactable: bool
    needs_human_review: bool
    review_reasons: list[str]
    recommended_action: RecommendedAction | None
    field_confidence: dict[str, float]
    safety_warning: str | None
    processing_error: str | None
    processing_attempts: int
    processed_at: datetime | None
    exported_at: datetime | None
    duplicate_of_id: UUID | None
    attachments: list[IntakeAttachmentResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedIntakeResponse(BaseModel):
    items: list[IntakeItemResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class IntakeReviewRequest(BaseModel):
    decision: IntakeReviewDecision
    customer_name: str | None = Field(default=None, max_length=255)
    customer_company: str | None = Field(default=None, max_length=255)
    customer_email: EmailStr | None = None
    customer_phone: str | None = Field(default=None, max_length=50)
    service_address: ServiceAddress | None = None
    service_requested: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=10_000)
    urgency: IntakeUrgency | None = None
    preferred_time: str | None = Field(default=None, max_length=500)
    inquiry_kind: IntakeKind | None = None
    inquiry_scope: IntakeScope | None = None
    recommended_action: RecommendedAction | None = None


class IntakeSetupResponse(BaseModel):
    email_enabled: bool
    inbound_email: str | None


def build_paginated_intake_response(
    *,
    items: list[IntakeItem],
    page: int,
    page_size: int,
    total: int,
) -> PaginatedIntakeResponse:
    return PaginatedIntakeResponse(
        items=[IntakeItemResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=math.ceil(total / page_size) if total else 0,
    )
