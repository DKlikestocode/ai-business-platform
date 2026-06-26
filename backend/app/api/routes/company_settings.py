from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    RateLimit,
    get_company_service,
    get_current_tenant_id,
    get_current_user,
    get_notification_service,
    get_settings,
)
from app.api.schemas.companies import (
    CompanySettingsResponse,
    CompanySettingsUpdateRequest,
    company_to_settings_response,
)
from app.config import Settings
from app.db.models.user import User
from app.domain.exceptions import NotFoundError
from app.services.notifications.email_delivery import get_email_delivery_status
from app.services.notifications.recipient import resolve_notification_recipient
from app.services.notifications.service import NotificationService
from app.services.tenant_service import CompanyService

router = APIRouter(prefix="/company", tags=["company"])

_test_notification_rate_limit = RateLimit(
    limit=5,
    window_seconds=60,
    scope="test_notification",
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
