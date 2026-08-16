from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.dependencies import (
    get_company_repository,
    get_current_tenant_id,
    get_current_user,
    get_intake_service,
)
from app.api.schemas.intake import (
    IntakeItemResponse,
    IntakeReviewRequest,
    IntakeSetupResponse,
    PaginatedIntakeResponse,
    build_paginated_intake_response,
)
from app.config import Settings, get_settings
from app.db.models.user import User
from app.repositories.company_repository import CompanyRepository
from app.services.intake.models import IntakeStatus
from app.services.intake.service import IntakeService

router = APIRouter(prefix="/intake-items", tags=["intake"])


@router.get(
    "/setup",
    response_model=IntakeSetupResponse,
    summary="Get the current company's inbound email setup",
)
def get_intake_setup(
    company_id: UUID = Depends(get_current_tenant_id),
    company_repository: CompanyRepository = Depends(get_company_repository),
    settings: Settings = Depends(get_settings),
    _: User = Depends(get_current_user),
) -> IntakeSetupResponse:
    company = company_repository.get_by_id(company_id)
    domain = settings.resend_inbound_domain.strip().lower().rstrip(".")
    enabled = settings.intake_email_enabled and bool(domain)
    return IntakeSetupResponse(
        email_enabled=enabled,
        inbound_email=f"{company.slug}@{domain}" if enabled and company else None,
    )


@router.get("", response_model=PaginatedIntakeResponse, summary="List intake items")
def list_intake_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: IntakeStatus | None = Query(None, alias="status"),
    company_id: UUID = Depends(get_current_tenant_id),
    service: IntakeService = Depends(get_intake_service),
    _: User = Depends(get_current_user),
) -> PaginatedIntakeResponse:
    items, total = service.list_items(
        company_id=company_id,
        page=page,
        page_size=page_size,
        status=status_filter,
    )
    return build_paginated_intake_response(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/{item_id}",
    response_model=IntakeItemResponse,
    summary="Get intake item by ID",
)
def get_intake_item(
    item_id: UUID,
    company_id: UUID = Depends(get_current_tenant_id),
    service: IntakeService = Depends(get_intake_service),
    _: User = Depends(get_current_user),
) -> IntakeItemResponse:
    item = service.get_item(item_id, company_id=company_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intake item '{item_id}' not found.",
        )
    return IntakeItemResponse.model_validate(item)


@router.patch(
    "/{item_id}/review",
    response_model=IntakeItemResponse,
    summary="Correct and approve an intake item",
)
def review_intake_item(
    item_id: UUID,
    payload: IntakeReviewRequest,
    company_id: UUID = Depends(get_current_tenant_id),
    service: IntakeService = Depends(get_intake_service),
    _: User = Depends(get_current_user),
) -> IntakeItemResponse:
    fields = payload.model_dump(
        mode="python",
        exclude_unset=True,
        exclude={"decision"},
    )
    try:
        item = service.review_item(
            item_id,
            company_id=company_id,
            fields=fields,
            decision=payload.decision,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if item is None:
        raise _not_found(item_id)
    return IntakeItemResponse.model_validate(item)


@router.post(
    "/{item_id}/retry",
    response_model=IntakeItemResponse,
    summary="Retry a failed intake item",
)
def retry_intake_item(
    item_id: UUID,
    company_id: UUID = Depends(get_current_tenant_id),
    service: IntakeService = Depends(get_intake_service),
    _: User = Depends(get_current_user),
) -> IntakeItemResponse:
    try:
        item = service.retry_item(item_id, company_id=company_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if item is None:
        raise _not_found(item_id)
    return IntakeItemResponse.model_validate(item)


@router.get(
    "/{item_id}/source.eml",
    response_model=None,
    summary="Download the original email",
)
def download_intake_source(
    item_id: UUID,
    company_id: UUID = Depends(get_current_tenant_id),
    service: IntakeService = Depends(get_intake_service),
    _: User = Depends(get_current_user),
) -> Response:
    content = service.source_document(item_id, company_id=company_id)
    if content is None:
        raise _not_found(item_id)
    return Response(
        content=content,
        media_type="message/rfc822",
        headers={"Content-Disposition": f'attachment; filename="{item_id}.eml"'},
    )


@router.get(
    "/{item_id}/attachments/{attachment_id}",
    response_model=None,
    summary="Download an intake attachment",
)
def download_intake_attachment(
    item_id: UUID,
    attachment_id: UUID,
    company_id: UUID = Depends(get_current_tenant_id),
    service: IntakeService = Depends(get_intake_service),
    _: User = Depends(get_current_user),
) -> Response:
    result = service.attachment_content(
        attachment_id,
        item_id=item_id,
        company_id=company_id,
    )
    if result is None:
        raise _not_found(item_id)
    filename, content_type, content = result
    encoded_filename = quote(filename, safe="")
    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )


@router.get(
    "/{item_id}/export.csv",
    response_model=None,
    summary="Export an approved intake item as CSV",
)
def export_intake_item(
    item_id: UUID,
    company_id: UUID = Depends(get_current_tenant_id),
    service: IntakeService = Depends(get_intake_service),
    _: User = Depends(get_current_user),
) -> Response:
    try:
        content = service.export_csv(item_id, company_id=company_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if content is None:
        raise _not_found(item_id)
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="auftrag-{item_id}.csv"'
        },
    )


def _not_found(item_id: UUID) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Intake item '{item_id}' not found.",
    )
