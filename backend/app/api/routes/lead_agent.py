from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.agents.lead_agent.models import LeadMessageRequest, LeadMessageResponse
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import get_current_tenant_id, get_current_user, get_lead_capture_service
from app.db.models.user import User

router = APIRouter(prefix="/agents/lead", tags=["lead-agent"])


@router.post(
    "/message",
    response_model=LeadMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the Lead Capture Agent",
)
async def send_lead_message(
    payload: LeadMessageRequest,
    company_id: UUID = Depends(get_current_tenant_id),
    service: LeadCaptureService = Depends(get_lead_capture_service),
    _: User = Depends(get_current_user),
) -> LeadMessageResponse:
    return await service.handle_message(payload, company_id=company_id)
