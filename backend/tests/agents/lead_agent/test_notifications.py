import pytest

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput, LeadMessageRequest, QualificationStatus
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
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
) -> LeadCaptureService:
    return LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=conversation_repository,
        extraction_client=MockLeadExtractionClient(outputs),
        repository=lead_repository,
        company_repository=company_repository,
        activation_repository=company_activation_repository,
        notification_service=notification_service,
    )


@pytest.mark.asyncio
async def test_lead_capture_sends_notification_when_lead_becomes_qualified(
    conversation_repository: ConversationRepository,
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
    company_activation_repository: CompanyActivationRepository,
    company,
) -> None:
    provider = MockEmailProvider()
    notification_service = NotificationService(provider, lead_repository)
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        notification_service=notification_service,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks, we have everything we need.",
                summary="Jane needs HVAC repair urgently.",
                name="Jane Doe",
                phone="01701234567",
                location="Austin, TX",
                service_requested="HVAC repair",
                description="AC not cooling",
                urgency="high",
                preferred_callback_time="Tomorrow morning",
            ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="notify-complete-conv",
            message="I need urgent HVAC repair tomorrow morning.",
        ),
        company_id=company.id,
    )

    assert response.qualification_status == QualificationStatus.QUALIFIED
    assert len(provider.messages) == 1
    lead = lead_repository.get_by_conversation("notify-complete-conv", company_id=company.id)
    assert lead is not None
    assert lead.notification_sent_at is not None


@pytest.mark.asyncio
async def test_lead_capture_does_not_send_notification_for_incomplete_lead(
    conversation_repository: ConversationRepository,
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
    company_activation_repository: CompanyActivationRepository,
    company,
) -> None:
    provider = MockEmailProvider()
    notification_service = NotificationService(provider, lead_repository)
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        notification_service=notification_service,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks! What service do you need?",
                urgency="high",
            ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="notify-incomplete-conv",
            message="I need urgent help",
        ),
        company_id=company.id,
    )

    assert response.qualification_status == QualificationStatus.INCOMPLETE
    assert provider.messages == []


@pytest.mark.asyncio
async def test_lead_capture_does_not_duplicate_notification(
    conversation_repository: ConversationRepository,
    lead_repository: LeadRepository,
    company_repository: CompanyRepository,
    company_activation_repository: CompanyActivationRepository,
    company,
) -> None:
    provider = MockEmailProvider()
    notification_service = NotificationService(provider, lead_repository)
    complete_output = LeadCaptureLLMOutput(
        reply="Thanks, we have everything we need.",
        summary="Jane needs HVAC repair urgently.",
        name="Jane Doe",
        phone="01701234567",
        location="Austin, TX",
        service_requested="HVAC repair",
        description="AC not cooling",
        urgency="high",
        preferred_callback_time="Tomorrow morning",
    )
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        notification_service=notification_service,
        outputs=[complete_output, complete_output],
    )

    first = await service.handle_message(
        LeadMessageRequest(
            conversation_id="notify-duplicate-conv",
            message="I need urgent HVAC repair tomorrow morning.",
        ),
        company_id=company.id,
    )
    second = await service.handle_message(
        LeadMessageRequest(
            conversation_id="notify-duplicate-conv",
            message="Thanks, tomorrow morning works.",
        ),
        company_id=company.id,
    )

    assert first.qualification_status == QualificationStatus.QUALIFIED
    assert second.qualification_status == QualificationStatus.QUALIFIED
    assert len(provider.messages) == 1
