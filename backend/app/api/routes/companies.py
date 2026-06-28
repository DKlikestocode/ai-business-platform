from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_company_service, get_current_user, require_registration_enabled
from app.api.schemas.companies import CompanyCreateRequest, CompanyResponse, company_to_response
from app.db.models.user import User
from app.domain.exceptions import NotFoundError
from app.services.tenant_service import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a company",
    dependencies=[Depends(require_registration_enabled)],
)
def create_company(
    payload: CompanyCreateRequest,
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    company = service.create_company(
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
    )
    return company_to_response(company)


@router.get("/{company_id}", response_model=CompanyResponse, summary="Get company by ID")
def get_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    if company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{company_id}' not found.",
        )

    try:
        company = service.get_company(company_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return company_to_response(company)
