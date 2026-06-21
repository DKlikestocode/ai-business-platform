import pytest

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput, LeadMessageRequest, QualificationStatus
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.db.models.enums import ConversationChannel
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.notifications.service import NotificationService
from tests.agents.lead_agent.conftest import MockLeadExtractionClient
from tests.services.test_notification_service import MockEmailProvider


def build_service(
    *,
    conversation_repository: ConversationRepository,
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
    company_activation_repository: CompanyActivationRepository,
    notification_service: NotificationService,
    outputs: list[LeadCaptureLLMOutput],
    channel: ConversationChannel = ConversationChannel.WEB,
) -> LeadCaptureService:
    return LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=conversation_repository,
        extraction_client=MockLeadExtractionClient(outputs),
        repository=lead_repository,
        company_repository=company_repository,
        activation_repository=company_activation_repository,
        notification_service=notification_service,
        channel=channel,
    )


@pytest.mark.asyncio
async def test_non_contactable_urgent_message_does_not_notify(
    conversation_repository: ConversationRepository,
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
    company_activation_repository: CompanyActivationRepository,
    company,
) -> None:
    provider = MockEmailProvider()
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        notification_service=NotificationService(provider, lead_repository),
        outputs=[
            LeadCaptureLLMOutput(
                reply="How can we reach you?",
                urgency="high",
                description="Need urgent help",
            ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="notify-non-contactable",
            message="I need urgent help right now",
        ),
        company_id=company.id,
    )

    assert response.contactable is False
    assert response.qualification_status == QualificationStatus.INCOMPLETE
    assert provider.messages == []
    assert lead_repository.get_by_conversation("notify-non-contactable", company_id=company.id) is None


@pytest.mark.asyncio
async def test_contactable_partial_lead_notifies_above_threshold(
    conversation_repository: ConversationRepository,
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
    company_activation_repository: CompanyActivationRepository,
    company,
) -> None:
    provider = MockEmailProvider()
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        notification_service=NotificationService(provider, lead_repository),
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks, we received your request.",
                phone="555-0100",
                description="Roof is leaking badly",
                location="Berlin",
            ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="notify-contactable-partial",
            message="My roof is leaking in Berlin, call me at 555-0100",
        ),
        company_id=company.id,
    )

    assert response.contactable is True
    assert response.qualification_status == QualificationStatus.CONTACTABLE
    assert response.lead_score >= 50
    assert len(provider.messages) == 1
    lead = lead_repository.get_by_conversation("notify-contactable-partial", company_id=company.id)
    assert lead is not None
    assert lead.notification_sent_at is not None


@pytest.mark.asyncio
async def test_contactable_low_score_lead_does_not_notify(
    conversation_repository: ConversationRepository,
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
    company_activation_repository: CompanyActivationRepository,
    company,
) -> None:
    provider = MockEmailProvider()
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        notification_service=NotificationService(provider, lead_repository),
        outputs=[LeadCaptureLLMOutput(reply="Thanks!", phone="555-0100")],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="notify-low-score",
            message="My number is 555-0100",
        ),
        company_id=company.id,
    )

    assert response.contactable is True
    assert response.qualification_status == QualificationStatus.INCOMPLETE
    assert response.lead_score == 25
    assert provider.messages == []
    assert lead_repository.get_by_conversation("notify-low-score", company_id=company.id) is None


@pytest.mark.asyncio
async def test_complete_lead_notifies(
    conversation_repository: ConversationRepository,
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
    company_activation_repository: CompanyActivationRepository,
    company,
) -> None:
    provider = MockEmailProvider()
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        notification_service=NotificationService(provider, lead_repository),
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks, we have everything we need.",
                summary="Qualified lead",
                name="Jane Doe",
                phone="555-0100",
                location="Berlin",
                service_requested="Roof repair",
                description="Leak in kitchen",
                urgency="high",
                preferred_callback_time="Tomorrow morning",
            ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="notify-qualified",
            message="Full details in one message",
        ),
        company_id=company.id,
    )

    assert response.qualification_status == QualificationStatus.QUALIFIED
    assert len(provider.messages) == 1


@pytest.mark.asyncio
async def test_whatsapp_channel_notifies_for_contactable_context(
    conversation_repository: ConversationRepository,
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
    company_activation_repository: CompanyActivationRepository,
    company,
) -> None:
    provider = MockEmailProvider()
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        notification_service=NotificationService(provider, lead_repository),
        channel=ConversationChannel.WHATSAPP,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks, we received your WhatsApp request.",
                description="Kitchen leak",
                location="Berlin",
            ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="notify-whatsapp",
            message="Kitchen leak in Berlin",
        ),
        company_id=company.id,
    )

    assert response.contactable is True
    assert response.lead_score >= 50
    assert len(provider.messages) == 1
