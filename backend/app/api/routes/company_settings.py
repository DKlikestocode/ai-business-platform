from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import (
    RateLimit,
    get_company_service,
    get_current_tenant_id,
    get_current_user,
    get_notification_service,
    get_settings,
    get_voice_lead_capture_service,
)
from app.api.schemas.companies import (
    CompanySettingsResponse,
    CompanySettingsUpdateRequest,
    company_to_settings_response,
)
from app.api.schemas.voice import TestVoiceIntakeResponse
from app.config import Settings
from app.db.models.user import User
from app.domain.exceptions import NotFoundError
from app.services.notifications.email_delivery import get_email_delivery_status
from app.services.notifications.recipient import resolve_notification_recipient
from app.services.notifications.service import NotificationService
from app.services.tenant_service import CompanyService
from app.services.voice.test_intake import (
    TEST_VOICE_CALLER_PHONE,
    build_dashboard_test_voice_request,
)

router = APIRouter(prefix="/company", tags=["company"])

_test_notification_rate_limit = RateLimit(
    limit=5,
    window_seconds=60,
    scope="test_notification",
)

_test_voice_intake_rate_limit = RateLimit(
    limit=5,
    window_seconds=60,
    scope="test_voice_intake",
)


@router.get(
    "/settings",
    response_model=CompanySettingsResponse,
    summary="Get current company settings",
)
def get_company_settings(
    company_id: UUID = Depends(get_current_tenant_id),
    service: CompanyService = Depends(get_company_service),
    settings: Settings = Depends(get_settings),
    _: User = Depends(get_current_user),
) -> CompanySettingsResponse:
    try:
        company = service.get_settings(company_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return company_to_settings_response(
        company,
        email_delivery=get_email_delivery_status(settings),
    )


@router.patch(
    "/settings",
    response_model=CompanySettingsResponse,
    summary="Update current company settings",
)
def update_company_settings(
    payload: CompanySettingsUpdateRequest,
    company_id: UUID = Depends(get_current_tenant_id),
    service: CompanyService = Depends(get_company_service),
    settings: Settings = Depends(get_settings),
    _: User = Depends(get_current_user),
) -> CompanySettingsResponse:
    updates = payload.model_dump(exclude_unset=True)
    try:
        company = service.update_settings(company_id, updates=updates)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return company_to_settings_response(
        company,
        email_delivery=get_email_delivery_status(settings),
    )


@router.post(
    "/settings/test-notification",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Send a test inquiry notification email",
    dependencies=[Depends(_test_notification_rate_limit)],
)
async def send_test_notification(
    company_id: UUID = Depends(get_current_tenant_id),
    company_service: CompanyService = Depends(get_company_service),
    notification_service: NotificationService = Depends(get_notification_service),
    _: User = Depends(get_current_user),
) -> None:
    try:
        company = company_service.get_settings(company_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if not resolve_notification_recipient(company):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No notification email configured.",
        )

    try:
        await notification_service.send_test_inquiry_notification(company)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to send test email. Check server email configuration.",
        ) from exc


@router.post(
    "/settings/test-voice-intake",
    response_model=TestVoiceIntakeResponse,
    summary="Simulate a phone inquiry into the inbox (dashboard test only)",
    dependencies=[Depends(_test_voice_intake_rate_limit)],
)
async def send_test_voice_intake(
    company_id: UUID = Depends(get_current_tenant_id),
    company_service: CompanyService = Depends(get_company_service),
    voice_service: LeadCaptureService = Depends(get_voice_lead_capture_service),
    _: User = Depends(get_current_user),
) -> TestVoiceIntakeResponse:
    try:
        company_service.get_settings(company_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    request = build_dashboard_test_voice_request()
    try:
        response = await voice_service.handle_message(
            request,
            company_id=company_id,
            caller_phone=TEST_VOICE_CALLER_PHONE,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to simulate voice intake. Check server configuration.",
        ) from exc

    return TestVoiceIntakeResponse(
        reply=response.reply,
        lead_id=response.lead_id,
    )
