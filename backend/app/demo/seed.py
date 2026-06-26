from uuid import UUID

from pydantic import BaseModel, Field

from app.agents.lead_agent.repository import LeadRepository
from app.demo.data import DEMO_CONVERSATION_IDS, DEMO_LEAD_SEEDS, DemoLeadSeed
from app.demo.service_area import ensure_company_service_area_for_examples
from app.repositories.company_repository import CompanyRepository
from app.services.service_area.evaluate import evaluate_service_area

DEMO_COMPANY_SLUG = "demo-company"


class SeedDemoDataResult(BaseModel):
    created: int
    skipped: int
    deleted: int = 0
    lead_ids: list[str] = Field(default_factory=list)
    message: str


def get_or_create_demo_company(repository: CompanyRepository):
    company = repository.get_by_slug(DEMO_COMPANY_SLUG)
    if company is not None:
        return company
    return repository.create(
        name="Demo Company",
        email="demo@example.com",
        phone="+49 30 123456",
        slug=DEMO_COMPANY_SLUG,
    )


def seed_demo_leads(
    repository: LeadRepository,
    *,
    company_id: UUID | None = None,
    company_repository: CompanyRepository | None = None,
) -> SeedDemoDataResult:
    """Replace existing demo leads and insert five fresh example inquiries."""
    if company_id is None:
        if company_repository is None:
            raise ValueError("company_id or company_repository is required.")
        company = get_or_create_demo_company(company_repository)
        company_id = company.id
    elif company_repository is not None:
        company = company_repository.get_by_id(company_id)
        if company is None:
            raise ValueError(f"Company '{company_id}' not found.")
    else:
        company = None

    if company_repository is not None and company is not None:
        company = ensure_company_service_area_for_examples(company_repository, company)

    deleted = repository.delete_by_conversation_ids(
        DEMO_CONVERSATION_IDS,
        company_id=company_id,
    )

    created_ids: list[str] = []

    for seed in DEMO_LEAD_SEEDS:
        service_area = (
            evaluate_service_area(company, seed.data) if company is not None else None
        )
        lead = repository.create_demo(
            company_id=company_id,
            conversation_id=seed.conversation_id,
            data=seed.data,
            summary=seed.summary,
            status=seed.status,
            service_area=service_area,
        )
        created_ids.append(str(lead.id))

    created = len(created_ids)
    message = (
        f"Replaced demo leads: removed {deleted}, created {created} example inquiry(ies)."
    )
    return SeedDemoDataResult(
        created=created,
        skipped=0,
        deleted=deleted,
        lead_ids=created_ids,
        message=message,
    )


def get_demo_seed(conversation_id: str) -> DemoLeadSeed | None:
    for seed in DEMO_LEAD_SEEDS:
        if seed.conversation_id == conversation_id:
            return seed
    return None
