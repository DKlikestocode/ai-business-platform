from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_company_service, get_current_tenant_id, get_current_user
from app.api.schemas.companies import (
    CompanySettingsResponse,
    CompanySettingsUpdateRequest,
    company_to_settings_response,
)
from app.db.models.user import User
from app.domain.exceptions import NotFoundError
from app.services.tenant_service import CompanyService

router = APIRouter(prefix="/company", tags=["company"])


@router.get(
    "/settings",
    response_model=CompanySettingsResponse,
    summary="Get current company settings",
)
def get_company_settings(
    company_id: UUID = Depends(get_current_tenant_id),
    service: CompanyService = Depends(get_company_service),
    _: User = Depends(get_current_user),
) -> CompanySettingsResponse:
    try:
        company = service.get_settings(company_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return company_to_settings_response(company)


@router.patch(
    "/settings",
    response_model=CompanySettingsResponse,
    summary="Update current company settings",
)
def update_company_settings(
    payload: CompanySettingsUpdateRequest,
    company_id: UUID = Depends(get_current_tenant_id),
    service: CompanyService = Depends(get_company_service),
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
    return company_to_settings_response(company)
