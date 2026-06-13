from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_activation_service, get_current_tenant_id, get_current_user
from app.api.schemas.activation import (
    ActivationResponse,
    ActivationUpdateRequest,
    activation_to_response,
)
from app.db.models.user import User
from app.domain.exceptions import NotFoundError
from app.services.activation.service import ActivationService

router = APIRouter(prefix="/company", tags=["company-activation"])


@router.get(
    "/activation",
    response_model=ActivationResponse,
    summary="Get current company activation state",
)
def get_company_activation(
    company_id: UUID = Depends(get_current_tenant_id),
    service: ActivationService = Depends(get_activation_service),
    _: User = Depends(get_current_user),
) -> ActivationResponse:
    try:
        view = service.get_activation(company_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return activation_to_response(view)


@router.patch(
    "/activation",
    response_model=ActivationResponse,
    summary="Update company activation settings",
)
def update_company_activation(
    payload: ActivationUpdateRequest,
    company_id: UUID = Depends(get_current_tenant_id),
    service: ActivationService = Depends(get_activation_service),
    _: User = Depends(get_current_user),
) -> ActivationResponse:
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        try:
            view = service.get_activation(company_id)
        except NotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        return activation_to_response(view)

    if "website_url" not in updates:
        try:
            view = service.get_activation(company_id)
        except NotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        return activation_to_response(view)

    try:
        view = service.update_website_url(
            company_id,
            website_url=updates["website_url"],
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return activation_to_response(view)
