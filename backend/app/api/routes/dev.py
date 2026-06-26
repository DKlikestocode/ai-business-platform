from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.lead_agent.repository import LeadRepository
from app.api.dependencies import (
    get_company_repository,
    get_lead_repository,
    get_optional_current_user,
)
from app.db.models.user import User
from app.api.schemas.companies import CompanyResponse, company_to_response
from app.config import Settings, get_settings
from app.demo.seed import SeedDemoDataResult, get_or_create_demo_company, seed_demo_leads
from app.repositories.company_repository import CompanyRepository

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post(
    "/seed-demo-data",
    response_model=SeedDemoDataResult,
    summary="Create demo leads (development only)",
)
def seed_demo_data(
    settings: Settings = Depends(get_settings),
    repository: LeadRepository = Depends(get_lead_repository),
    company_repository: CompanyRepository = Depends(get_company_repository),
    current_user: User | None = Depends(get_optional_current_user),
) -> SeedDemoDataResult:
    if not settings.is_development:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if current_user is not None:
        return seed_demo_leads(
            repository,
            company_id=current_user.company_id,
            company_repository=company_repository,
        )

    return seed_demo_leads(repository, company_repository=company_repository)


@router.post(
    "/demo-company",
    response_model=CompanyResponse,
    summary="Get or create the development demo company",
)
def bootstrap_demo_company(
    settings: Settings = Depends(get_settings),
    company_repository: CompanyRepository = Depends(get_company_repository),
) -> CompanyResponse:
    if not settings.is_development:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    company = get_or_create_demo_company(company_repository)
    return company_to_response(company)
