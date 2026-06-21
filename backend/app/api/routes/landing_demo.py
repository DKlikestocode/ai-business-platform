from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.lead_agent.models import LeadMessageRequest, LeadMessageResponse
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import (
    RateLimit,
    get_company_repository,
    get_conversation_repository,
    get_landing_demo_lead_capture_service,
)
from app.api.schemas.landing_demo import LandingDemoMessageRequest
from app.config import Settings, get_settings
from app.demo.seed import get_or_create_demo_company
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.landing_demo.service import LandingDemoLimitError, ensure_landing_demo_message_allowed

router = APIRouter(prefix="/public", tags=["public-landing-demo"])

_landing_demo_rate_limit = RateLimit(limit=20, window_seconds=60, scope="landing_demo")
_LANDING_DEMO_LIMIT_DETAIL = (
    "Diese Demo ist beendet. Starten Sie eine neue Demo oder registrieren Sie Ihren Betrieb."
)


@router.post(
    "/landing-demo/message",
    response_model=LeadMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message in the marketing landing page demo chat",
    dependencies=[Depends(_landing_demo_rate_limit)],
)
async def send_landing_demo_message(
    payload: LandingDemoMessageRequest,
    service: LeadCaptureService = Depends(get_landing_demo_lead_capture_service),
    company_repository: CompanyRepository = Depends(get_company_repository),
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
    settings: Settings = Depends(get_settings),
) -> LeadMessageResponse:
    company = get_or_create_demo_company(company_repository)

    try:
        ensure_landing_demo_message_allowed(
            conversation_repository=conversation_repository,
            company_id=company.id,
            conversation_external_id=payload.conversation_id,
            settings=settings,
        )
    except LandingDemoLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=_LANDING_DEMO_LIMIT_DETAIL,
        ) from None

    lead_request = LeadMessageRequest(
        conversation_id=payload.conversation_id,
        message=payload.message,
    )
    return await service.handle_message(lead_request, company_id=company.id)
