from app.agents.lead_agent.repository import LeadRepository
from app.demo.data import DEMO_LEAD_SEEDS
from app.demo.seed import seed_demo_leads
from app.repositories.company_repository import CompanyRepository


def test_seed_demo_leads_creates_all_scenarios(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    result = seed_demo_leads(lead_repository, company_repository=company_repository)

    assert result.created + result.skipped == len(DEMO_LEAD_SEEDS)

    for seed in DEMO_LEAD_SEEDS:
        lead = lead_repository.get_by_conversation(seed.conversation_id)
        assert lead is not None
        assert lead.name == seed.data.name
        assert lead.status == seed.status.value


def test_seed_demo_leads_skips_existing_records(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    first = seed_demo_leads(lead_repository, company_repository=company_repository)
    second = seed_demo_leads(lead_repository, company_repository=company_repository)

    assert first.created + first.skipped == len(DEMO_LEAD_SEEDS)
    assert second.created == 0
    assert second.skipped == len(DEMO_LEAD_SEEDS)
