from uuid import UUID

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.agents.lead_agent.dashboard_service import LeadDashboardService
from app.agents.lead_agent.models import InquiryKind, LeadStatus, QualificationStatus
from app.agents.lead_agent.repository import LeadRepository
from app.api.dependencies import (
    get_company_repository,
    get_current_tenant_id,
    get_current_user,
    get_lead_dashboard_service,
    get_lead_repository,
    get_notification_service,
    get_settings,
)
from app.api.schemas.leads import (
    AppointmentConfirmationRequest,
    AppointmentConfirmationResponse,
    BulkDeleteLeadsResponse,
    LeadResponse,
    LeadStatusUpdateRequest,
    PaginatedLeadResponse,
)
from app.config import Settings
from app.db.models.user import User
from app.repositories.company_repository import CompanyRepository
from app.services.calendar.ics import build_lead_calendar_ics
from app.services.notifications.service import NotificationService

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=PaginatedLeadResponse, summary="List leads")
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: LeadStatus | None = Query(None),
    qualification_status: QualificationStatus | None = Query(None),
    contactable: bool | None = Query(None),
    sort: Literal["created_at_desc", "urgency_desc"] = Query("urgency_desc"),
    inquiry_kind: InquiryKind | None = Query(
        None,
        description=(
            "Filter by inquiry category. "
            "appointment_consultation includes unknown/unclassified leads."
        ),
    ),
    archived: bool = Query(
        False,
        description="When true, return contacted inquiries (status != new).",
    ),
    company_id: UUID = Depends(get_current_tenant_id),
    service: LeadDashboardService = Depends(get_lead_dashboard_service),
    _: User = Depends(get_current_user),
) -> PaginatedLeadResponse:
    return service.list_leads(
        page=page,
        page_size=page_size,
        status=status,
        qualification_status=qualification_status,
        contactable=contactable,
        sort=sort,
        company_id=company_id,
        archived=archived,
        inquiry_kind=inquiry_kind.value if inquiry_kind is not None else None,
    )


@router.delete(
    "/contacted",
    response_model=BulkDeleteLeadsResponse,
    summary="Delete all contacted inquiries",
)
def delete_contacted_leads(
    contactable: bool | None = Query(None),
    company_id: UUID = Depends(get_current_tenant_id),
    service: LeadDashboardService = Depends(get_lead_dashboard_service),
    _: User = Depends(get_current_user),
) -> BulkDeleteLeadsResponse:
    deleted = service.delete_contacted_leads(
        company_id=company_id,
        contactable=contactable,
    )
    return BulkDeleteLeadsResponse(deleted=deleted)


@router.get("/{lead_id}", response_model=LeadResponse, summary="Get lead by ID")
def get_lead(
    lead_id: UUID,
    company_id: UUID = Depends(get_current_tenant_id),
    service: LeadDashboardService = Depends(get_lead_dashboard_service),
    _: User = Depends(get_current_user),
) -> LeadResponse:
    lead = service.get_lead(lead_id, company_id=company_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead '{lead_id}' not found.",
        )
    return lead


@router.get(
    "/{lead_id}/calendar.ics",
    summary="Download calendar event for lead appointment",
    response_class=Response,
)
def download_lead_calendar(
    lead_id: UUID,
    company_id: UUID = Depends(get_current_tenant_id),
    lead_repository: LeadRepository = Depends(get_lead_repository),
    company_repository: CompanyRepository = Depends(get_company_repository),
    settings: Settings = Depends(get_settings),
    _: User = Depends(get_current_user),
) -> Response:
    lead = lead_repository.get_by_id(lead_id, company_id=company_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead '{lead_id}' not found.",
        )

    company = company_repository.get_by_id(company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    ics_content = build_lead_calendar_ics(
        company=company,
        lead=lead,
        frontend_base_url=settings.frontend_base_url,
    )
    filename = f"termin-{lead_id}.ics"
    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/{lead_id}/appointment-confirmation",
    response_model=AppointmentConfirmationResponse,
    summary="Send appointment confirmation to customer",
)
async def send_appointment_confirmation(
    lead_id: UUID,
    payload: AppointmentConfirmationRequest,
    company_id: UUID = Depends(get_current_tenant_id),
    lead_repository: LeadRepository = Depends(get_lead_repository),
    company_repository: CompanyRepository = Depends(get_company_repository),
    notification_service: NotificationService = Depends(get_notification_service),
    _: User = Depends(get_current_user),
) -> AppointmentConfirmationResponse:
    if payload.channel == "sms":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SMS-Terminbestätigung ist noch nicht verfügbar.",
        )

    lead = lead_repository.get_by_id(lead_id, company_id=company_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead '{lead_id}' not found.",
        )

    if lead.appointment_confirmation_sent_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Terminbestätigung wurde bereits gesendet.",
        )

    company = company_repository.get_by_id(company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    from app.agents.lead_agent.contact_validation import is_valid_email

    if not is_valid_email(lead.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keine gültige E-Mail-Adresse für diese Anfrage hinterlegt.",
        )

    sent_at = await notification_service.send_appointment_confirmation_email(company, lead)
    if sent_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terminbestätigung konnte nicht gesendet werden.",
        )

    return AppointmentConfirmationResponse(
        sent=True,
        appointment_confirmation_sent_at=sent_at,
    )


@router.patch(
    "/{lead_id}/status",
    response_model=LeadResponse,
    summary="Update lead status",
)
def update_lead_status(
    lead_id: UUID,
    payload: LeadStatusUpdateRequest,
    company_id: UUID = Depends(get_current_tenant_id),
    service: LeadDashboardService = Depends(get_lead_dashboard_service),
    _: User = Depends(get_current_user),
) -> LeadResponse:
    lead = service.update_status(lead_id, payload.status, company_id=company_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead '{lead_id}' not found.",
        )
    return lead


@router.patch(
    "/{lead_id}/restore",
    response_model=LeadResponse,
    summary="Restore a contacted lead to the inbox",
)
def restore_lead(
    lead_id: UUID,
    company_id: UUID = Depends(get_current_tenant_id),
    service: LeadDashboardService = Depends(get_lead_dashboard_service),
    _: User = Depends(get_current_user),
) -> LeadResponse:
    lead = service.restore_lead(lead_id, company_id=company_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead '{lead_id}' not found.",
        )
    return lead


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a lead",
)
def delete_lead(
    lead_id: UUID,
    company_id: UUID = Depends(get_current_tenant_id),
    service: LeadDashboardService = Depends(get_lead_dashboard_service),
    _: User = Depends(get_current_user),
) -> None:
    deleted = service.delete_lead(lead_id, company_id=company_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead '{lead_id}' not found.",
        )
