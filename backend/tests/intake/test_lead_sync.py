import pytest

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput, LeadMessageRequest
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.db.models.enums import ConversationChannel
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.intake_repository import IntakeRepository
from app.services.intake.models import IntakeChannel, IntakeStatus
from app.services.notifications.service import NotificationService
from tests.agents.lead_agent.conftest import MockLeadExtractionClient
from tests.services.test_notification_service import MockEmailProvider


@pytest.mark.asyncio
async def test_website_lead_is_mirrored_into_unified_intake(
    db_session,
    company,
) -> None:
    lead_repository = LeadRepository(db_session)
    intake_repository = IntakeRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [
                LeadCaptureLLMOutput(
                    reply="Danke, wir melden uns.",
                    summary="Angebot für eine neue Heizung",
                    name="Maria Muster",
                    phone="01701234567",
                    email="maria@example.com",
                    location="Köln",
                    postal_code="50667",
                    service_requested="Heizung erneuern",
                    description="Alte Gasheizung soll ersetzt werden.",
                    urgency="mittel",
                    preferred_callback_time="Morgen Vormittag",
                    inquiry_kind="quote",
                )
            ]
        ),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        activation_repository=CompanyActivationRepository(db_session),
        notification_service=NotificationService(
            MockEmailProvider(),
            lead_repository,
        ),
        channel=ConversationChannel.WEB,
        intake_repository=intake_repository,
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="unified-intake-website-1",
            message="Bitte erstellen Sie mir ein Angebot für eine neue Heizung.",
        ),
        company_id=company.id,
    )

    assert response.lead_id is not None
    items, total = intake_repository.list_items(
        company_id=company.id,
        page=1,
        page_size=20,
    )
    assert total == 1
    assert items[0].channel == IntakeChannel.WEBSITE.value
    assert items[0].status == IntakeStatus.NEEDS_REVIEW.value
    assert items[0].customer_name == "Maria Muster"
    assert items[0].service_requested == "Heizung erneuern"
    assert items[0].recommended_action == "prepare_quote"


def test_dashboard_test_lead_is_not_mirrored(
    intake_repository: IntakeRepository,
    lead_repository: LeadRepository,
    company,
) -> None:
    from app.agents.lead_agent.models import LeadExtractedData

    lead = lead_repository.create(
        company_id=company.id,
        conversation_id="dashboard-test-only",
        data=LeadExtractedData(
            name="Test User",
            phone="01701234567",
            service_requested="Test",
            description="Nur ein Test",
        ),
        summary="Test",
    )

    result = intake_repository.sync_lead(
        lead,
        conversation_channel=ConversationChannel.DASHBOARD,
    )

    assert result is None
    _, total = intake_repository.list_items(
        company_id=company.id,
        page=1,
        page_size=20,
    )
    assert total == 0
