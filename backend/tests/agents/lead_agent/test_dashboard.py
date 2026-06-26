import pytest

from app.agents.lead_agent.dashboard_service import LeadDashboardService
from app.agents.lead_agent.models import LeadExtractedData, LeadStatus
from app.agents.lead_agent.repository import LeadRepository
from app.db.models.company import Company
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.conversation_repository import ConversationRepository


@pytest.fixture
def dashboard_service(
    lead_repository: LeadRepository,
    conversation_repository: ConversationRepository,
    company_activation_repository: CompanyActivationRepository,
) -> LeadDashboardService:
    return LeadDashboardService(
        lead_repository,
        conversation_repository,
        company_activation_repository,
    )


def test_repository_list_leads_paginates(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    _, total_before = lead_repository.list_leads(page=1, page_size=100)
    for index in range(3):
        lead_repository.create(
            company_id=company.id,
            conversation_id=f"repo-conv-{total_before}-{index}",
            data=LeadExtractedData(
                name=f"Lead {index}",
                phone="555",
                location="Austin",
                service_requested="HVAC",
                description="Test",
                urgency="low",
                preferred_callback_time="Afternoon",
            ),
            summary=None,
        )

    items, total = lead_repository.list_leads(page=1, page_size=2)
    assert total == total_before + 3
    assert len(items) == 2


def test_repository_filters_by_status(
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    lead = lead_repository.create(
        company_id=company.id,
        conversation_id=f"repo-filter-{lead_repository.list_leads(page=1, page_size=1)[1]}",
        data=LeadExtractedData(
            name="Filter Lead",
            phone="555",
            location="Austin",
            service_requested="HVAC",
            description="Test",
            urgency="low",
            preferred_callback_time="Afternoon",
        ),
        summary=None,
    )
    lead_repository.update_status(lead.id, LeadStatus.CONTACTED, company_id=company.id)

    items, total = lead_repository.list_leads(
        page=1,
        page_size=10,
        status=LeadStatus.CONTACTED,
        archived=True,
    )
    assert total >= 1
    assert any(item.id == lead.id for item in items)
    assert items[0].status == LeadStatus.CONTACTED.value


def test_dashboard_service_update_status(
    dashboard_service: LeadDashboardService,
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    lead = lead_repository.create(
        company_id=company.id,
        conversation_id="service-conv",
        data=LeadExtractedData(
            name="Service Lead",
            phone="555",
            location="Austin",
            service_requested="HVAC",
            description="Test",
            urgency="low",
            preferred_callback_time="Afternoon",
        ),
        summary=None,
    )

    updated = dashboard_service.update_status(lead.id, LeadStatus.CONTACTED, company_id=company.id)
    assert updated is not None
    assert updated.status == LeadStatus.CONTACTED
    assert updated.contacted_at is not None

    won = dashboard_service.update_status(lead.id, LeadStatus.WON, company_id=company.id)
    assert won is not None
    assert won.status == LeadStatus.WON
    assert won.archived_at is not None


def test_restore_lead_returns_to_active_inbox(
    dashboard_service: LeadDashboardService,
    lead_repository: LeadRepository,
    company: Company,
) -> None:
    lead = lead_repository.create(
        company_id=company.id,
        conversation_id="restore-conv",
        data=LeadExtractedData(
            name="Restore Lead",
            phone="555",
            location="Austin",
            service_requested="HVAC",
            description="Test",
            urgency="low",
            preferred_callback_time="Afternoon",
        ),
        summary=None,
    )
    dashboard_service.update_status(lead.id, LeadStatus.CONTACTED, company_id=company.id)

    active_before, _ = lead_repository.list_leads(page=1, page_size=10, company_id=company.id)
    assert all(item.id != lead.id for item in active_before)

    restored = dashboard_service.restore_lead(lead.id, company_id=company.id)
    assert restored is not None
    assert restored.archived_at is None

    active_after, _ = lead_repository.list_leads(page=1, page_size=10, company_id=company.id)
    assert any(item.id == lead.id for item in active_after)
