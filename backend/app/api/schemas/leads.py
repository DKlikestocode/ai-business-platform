import math
from datetime import datetime
from uuid import UUID

from typing import Literal

from pydantic import BaseModel

from app.agents.lead_agent.inquiry_source import (
    InquirySource,
    channel_to_inquiry_source,
)
from app.agents.lead_agent.models import ContactMethod, InquiryKind, LeadStatus, QualificationStatus
from app.db.models.enums import ConversationChannel
from app.db.models.lead import Lead
from app.services.service_area.models import ServiceAreaStatus


class LeadResponse(BaseModel):
    id: UUID
    company_id: UUID
    conversation_id: str
    source: InquirySource
    is_first_website_inquiry: bool
    name: str
    phone: str
    email: str | None
    company: str | None
    location: str
    postal_code: str | None
    service_area_status: ServiceAreaStatus | None = None
    service_area_distance_km: float | None = None
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
    inquiry_kind: InquiryKind
    notification_sent_at: datetime | None
    customer_confirmation_sent_at: datetime | None
    contacted_at: datetime | None
    archived_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedLeadResponse(BaseModel):
    items: list[LeadResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class LeadStatusUpdateRequest(BaseModel):
    status: Literal[LeadStatus.NEW, LeadStatus.CONTACTED]


class BulkDeleteLeadsResponse(BaseModel):
    deleted: int


def resolve_is_first_website_inquiry(
    lead: Lead,
    *,
    source: InquirySource,
    first_website_inquiry_lead_id: UUID | None,
) -> bool:
    if source != InquirySource.WEBSITE:
        return False
    if first_website_inquiry_lead_id is None:
        return False
    return lead.id == first_website_inquiry_lead_id


def lead_to_response(
    lead: Lead,
    *,
    source: InquirySource,
    first_website_inquiry_lead_id: UUID | None = None,
) -> LeadResponse:
    return LeadResponse.model_validate(
        {
            "id": lead.id,
            "company_id": lead.company_id,
            "conversation_id": lead.conversation_id,
            "source": source,
            "is_first_website_inquiry": resolve_is_first_website_inquiry(
                lead,
                source=source,
                first_website_inquiry_lead_id=first_website_inquiry_lead_id,
            ),
            "name": lead.name,
            "phone": lead.phone,
            "email": lead.email,
            "company": lead.company,
            "location": lead.location,
            "postal_code": lead.postal_code,
            "service_area_status": lead.service_area_status,
            "service_area_distance_km": lead.service_area_distance_km,
            "service_requested": lead.service_requested,
            "description": lead.description,
            "urgency": lead.urgency,
            "preferred_callback_time": lead.preferred_callback_time,
            "status": lead.status,
            "summary": lead.summary,
            "contactable": lead.contactable,
            "contact_method": lead.contact_method,
            "lead_score": lead.lead_score,
            "qualification_status": lead.qualification_status,
            "inquiry_kind": lead.inquiry_kind or InquiryKind.UNKNOWN.value,
            "notification_sent_at": lead.notification_sent_at,
            "customer_confirmation_sent_at": lead.customer_confirmation_sent_at,
            "contacted_at": lead.contacted_at,
            "archived_at": lead.archived_at,
            "created_at": lead.created_at,
        }
    )


def resolve_lead_source(
    lead: Lead,
    channels_by_conversation_id: dict[str, ConversationChannel],
) -> InquirySource:
    # Missing conversation rows default to Website for legacy/demo leads.
    channel = channels_by_conversation_id.get(lead.conversation_id)
    return channel_to_inquiry_source(channel)


def build_paginated_response(
    *,
    items: list[Lead],
    page: int,
    page_size: int,
    total: int,
    channels_by_conversation_id: dict[str, ConversationChannel],
    first_website_inquiry_lead_id: UUID | None = None,
) -> PaginatedLeadResponse:
    total_pages = math.ceil(total / page_size) if total else 0
    return PaginatedLeadResponse(
        items=[
            lead_to_response(
                lead,
                source=resolve_lead_source(lead, channels_by_conversation_id),
                first_website_inquiry_lead_id=first_website_inquiry_lead_id,
            )
            for lead in items
        ],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )
