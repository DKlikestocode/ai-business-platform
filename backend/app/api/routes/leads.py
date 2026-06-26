from uuid import UUID

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.agents.lead_agent.dashboard_service import LeadDashboardService
from app.agents.lead_agent.models import LeadStatus, QualificationStatus
from app.api.dependencies import (
    get_current_tenant_id,
    get_current_user,
    get_lead_dashboard_service,
)
from app.api.schemas.leads import LeadResponse, LeadStatusUpdateRequest, PaginatedLeadResponse
from app.db.models.user import User

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=PaginatedLeadResponse, summary="List leads")
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: LeadStatus | None = Query(None),
    qualification_status: QualificationStatus | None = Query(None),
    contactable: bool | None = Query(None),
    sort: Literal["created_at_desc", "lead_score_desc"] = Query("created_at_desc"),
    archived: bool = Query(False),
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
    )


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
    summary="Restore an archived lead to the inbox",
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
