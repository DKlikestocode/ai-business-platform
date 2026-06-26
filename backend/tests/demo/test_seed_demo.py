from app.agents.lead_agent.repository import LeadRepository
from app.demo.data import DEMO_LEAD_SEEDS
from app.demo.seed import get_or_create_demo_company, seed_demo_leads
from app.repositories.company_repository import CompanyRepository


def test_seed_demo_leads_creates_all_scenarios(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    company = company_repository.create(
        name="Demo Seed Scenarios Co",
        email="demo-scenarios@example.com",
    )
    result = seed_demo_leads(
        lead_repository,
        company_id=company.id,
        company_repository=company_repository,
    )

    assert result.created == len(DEMO_LEAD_SEEDS)
    assert result.skipped == 0

    for seed in DEMO_LEAD_SEEDS:
        lead = lead_repository.get_by_conversation(
            seed.conversation_id,
            company_id=company.id,
        )
        assert lead is not None
        assert lead.name == seed.data.name
        assert lead.status == seed.status.value
        assert lead.service_area_status in {"in_range", "out_of_range"}
        assert lead.archived_at is None


def test_create_demo_keeps_example_inquiries_in_active_inbox(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    company = company_repository.create(
        name="Demo Inbox Visibility Co",
        email="demo-inbox@example.com",
    )

    lead = lead_repository.create_demo(
        company_id=company.id,
        conversation_id="demo-dachdecker-001",
        data=DEMO_LEAD_SEEDS[0].data,
        summary=DEMO_LEAD_SEEDS[0].summary,
        status=DEMO_LEAD_SEEDS[1].status,
    )

    assert lead.status == DEMO_LEAD_SEEDS[1].status.value
    assert lead.archived_at is None


def test_seed_demo_leads_configures_service_area_when_missing(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    company = company_repository.create(
        name="Service Area Seed Co",
        email="service-area-seed@example.com",
    )

    seed_demo_leads(
        lead_repository,
        company_id=company.id,
        company_repository=company_repository,
    )

    company_repository._session.refresh(company)
    assert company.service_area_center == "22303 Hamburg"
    assert company.service_radius_km == 40
    assert company.service_area_latitude is not None


def test_seed_demo_leads_replaces_existing_records(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    company = get_or_create_demo_company(company_repository)
    first = seed_demo_leads(
        lead_repository,
        company_id=company.id,
        company_repository=company_repository,
    )
    second = seed_demo_leads(
        lead_repository,
        company_id=company.id,
        company_repository=company_repository,
    )

    assert first.created == len(DEMO_LEAD_SEEDS)
    assert first.skipped == 0
    assert second.created == len(DEMO_LEAD_SEEDS)
    assert second.skipped == 0
    assert second.deleted == len(DEMO_LEAD_SEEDS)


def test_seed_demo_leads_allows_same_conversation_ids_per_company(
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
) -> None:
    company_a = get_or_create_demo_company(company_repository)
    company_b = company_repository.create(
        name="Second Demo Company",
        email="second-demo@example.com",
    )

    seed_demo_leads(
        lead_repository,
        company_id=company_a.id,
        company_repository=company_repository,
    )
    result_b = seed_demo_leads(
        lead_repository,
        company_id=company_b.id,
        company_repository=company_repository,
    )

    assert result_b.created == len(DEMO_LEAD_SEEDS)
    assert result_b.skipped == 0

    for seed in DEMO_LEAD_SEEDS:
        lead = lead_repository.get_by_conversation(
            seed.conversation_id,
            company_id=company_b.id,
        )
        assert lead is not None
