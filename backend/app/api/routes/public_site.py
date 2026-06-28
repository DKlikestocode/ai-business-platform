from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import RateLimit, get_company_repository
from app.api.schemas.public_site import PublicBusinessSiteResponse
from app.config import get_settings
from app.db.session import get_db
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository

router = APIRouter(prefix="/public", tags=["public-site"])

_site_rate_limit = RateLimit(limit=120, window_seconds=60, scope="public_site")


@router.get(
    "/site/{company_slug}",
    response_model=PublicBusinessSiteResponse,
    summary="Public business website profile and widget embed config",
    dependencies=[Depends(_site_rate_limit)],
)
def get_public_business_site(
    company_slug: str,
    company_repository: CompanyRepository = Depends(get_company_repository),
    db: Session = Depends(get_db),
) -> PublicBusinessSiteResponse:
    company = company_repository.get_by_slug(company_slug)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{company_slug}' not found.",
        )

    activation = CompanyActivationRepository(db).get_or_create(company.id)
    settings = get_settings()
    api_base = (settings.public_api_base_url or "https://api.example.com").rstrip("/")

    return PublicBusinessSiteResponse(
        company_name=company.name,
        company_slug=company.slug,
        email=company.email,
        phone=company.phone,
        trade=company.trade,
        service_area_center=company.service_area_center,
        service_radius_km=company.service_radius_km,
        widget_company_slug=company.slug,
        widget_api_base=api_base,
        widget_install_token=activation.install_token,
    )
