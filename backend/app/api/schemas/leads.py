import math
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.agents.lead_agent.models import ContactMethod, LeadStatus, QualificationStatus
from app.db.models.lead import Lead


class LeadResponse(BaseModel):
    id: UUID
    company_id: UUID
    conversation_id: str
    name: str
    phone: str
    email: str | None
    company: str | None
    location: str
    service_requested: str
    description: str
    urgency: str
    preferred_callback_time: str
    status: LeadStatus
    summary: str | None
    contactable: bool
    contact_method: ContactMethod | None = None
    lead_score: int
    qualification_status: QualificationStatus
    notification_sent_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedLeadResponse(BaseModel):
    items: list[LeadResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class LeadStatusUpdateRequest(BaseModel):
    status: LeadStatus


def lead_to_response(lead: Lead) -> LeadResponse:
    return LeadResponse.model_validate(lead)


def build_paginated_response(
    *,
    items: list[Lead],
    page: int,
    page_size: int,
    total: int,
) -> PaginatedLeadResponse:
    total_pages = math.ceil(total / page_size) if total else 0
    return PaginatedLeadResponse(
        items=[lead_to_response(lead) for lead in items],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )
