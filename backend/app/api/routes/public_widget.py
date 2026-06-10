from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.lead_agent.models import LeadMessageRequest, LeadMessageResponse
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import (
    RateLimit,
    get_company_repository,
    get_lead_capture_service,
)
from app.api.schemas.widget import WidgetMessageRequest
from app.repositories.company_repository import CompanyRepository

router = APIRouter(prefix="/public", tags=["public-widget"])

_widget_rate_limit = RateLimit(limit=30, window_seconds=60, scope="public_widget")


@router.post(
    "/widget/message",
    response_model=LeadMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message from the embeddable website widget",
    dependencies=[Depends(_widget_rate_limit)],
)
async def send_widget_message(
    payload: WidgetMessageRequest,
    service: LeadCaptureService = Depends(get_lead_capture_service),
    company_repository: CompanyRepository = Depends(get_company_repository),
) -> LeadMessageResponse:
    company = company_repository.get_by_slug(payload.company_slug)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{payload.company_slug}' not found.",
        )

    lead_request = LeadMessageRequest(
        conversation_id=payload.conversation_id,
        message=payload.message,
    )
    return await service.handle_message(lead_request, company_id=company.id)
