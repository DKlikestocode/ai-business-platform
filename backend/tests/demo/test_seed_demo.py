from app.agents.lead_agent.repository import LeadRepository
from app.demo.data import DEMO_LEAD_SEEDS
from app.demo.seed import get_or_create_demo_company, seed_demo_leads
from app.repositories.company_repository import CompanyRepository


def test_seed_demo_leads_creates_all_scenarios(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    result = seed_demo_leads(lead_repository, company_repository=company_repository)
    company = get_or_create_demo_company(company_repository)

    assert result.created + result.skipped == len(DEMO_LEAD_SEEDS)

    for seed in DEMO_LEAD_SEEDS:
        lead = lead_repository.get_by_conversation(
            seed.conversation_id,
            company_id=company.id,
        )
        assert lead is not None
        assert lead.name == seed.data.name
        assert lead.status == seed.status.value


def test_seed_demo_leads_skips_existing_records(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    company = get_or_create_demo_company(company_repository)
    first = seed_demo_leads(lead_repository, company_id=company.id)
    second = seed_demo_leads(lead_repository, company_id=company.id)

    assert first.created + first.skipped == len(DEMO_LEAD_SEEDS)
    assert second.created == 0
    assert second.skipped == len(DEMO_LEAD_SEEDS)


def test_seed_demo_leads_allows_same_conversation_ids_per_company(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    company_a = get_or_create_demo_company(company_repository)
    company_b = company_repository.create(
        name="Second Demo Company",
        email="second-demo@example.com",
    )

    seed_demo_leads(lead_repository, company_id=company_a.id)
    result_b = seed_demo_leads(lead_repository, company_id=company_b.id)

    assert result_b.created == len(DEMO_LEAD_SEEDS)
    assert result_b.skipped == 0

    for seed in DEMO_LEAD_SEEDS:
        lead = lead_repository.get_by_conversation(
            seed.conversation_id,
            company_id=company_b.id,
        )
        assert lead is not None
