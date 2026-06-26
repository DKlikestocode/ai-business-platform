import pytest

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput, LeadMessageRequest
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
    outputs: list[LeadCaptureLLMOutput],
) -> LeadCaptureService:
    return LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=conversation_repository,
        extraction_client=MockLeadExtractionClient(outputs),
        repository=lead_repository,
        company_repository=company_repository,
        activation_repository=company_activation_repository,
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
    )


@pytest.mark.asyncio
async def test_lead_capture_service_tracks_missing_fields(
    conversation_repository: ConversationRepository,
    lead_repository,
    company_repository,
    company_activation_repository,
    company,
) -> None:
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        outputs=[
                LeadCaptureLLMOutput(
                    reply="Thanks! What service do you need?",
                    name="Jane Doe",
                    phone="01701234567",
                ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="lead-conv-1",
            message="Hi, I'm Jane Doe at 01701234567 in Austin.",
        ),
        company_id=company.id,
    )

    assert response.lead_complete is False
    assert "service_requested" in response.missing_fields
    assert response.extracted_data.name == "Jane Doe"
    assert response.lead_id is None


@pytest.mark.asyncio
async def test_lead_capture_service_persists_complete_lead(
    conversation_repository: ConversationRepository,
    lead_repository,
    company_repository,
    company_activation_repository,
    company,
) -> None:
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks, we have everything we need.",
                summary="Jane needs HVAC repair urgently.",
                name="Jane Doe",
                phone="01701234567",
                location="Austin, TX",
                postal_code="10115",
                service_requested="HVAC repair",
                description="AC not cooling",
                urgency="high",
                preferred_callback_time="Tomorrow morning",
            ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="lead-conv-complete",
            message="I need urgent HVAC repair tomorrow morning.",
        ),
        company_id=company.id,
    )

    assert response.lead_complete is True
    assert response.missing_fields == []
    assert response.lead_id is not None

    lead = lead_repository.get_by_conversation("lead-conv-complete", company_id=company.id)
    assert lead is not None
    assert lead.name == "Jane Doe"
    assert lead.service_requested == "HVAC repair"


@pytest.mark.asyncio
async def test_lead_capture_service_merges_context_across_messages(
    conversation_repository: ConversationRepository,
    lead_repository,
    company_repository,
    company_activation_repository,
    company,
) -> None:
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks Jane. What service do you need?",
                name="Jane Doe",
                phone="01701234567",
            ),
            LeadCaptureLLMOutput(
                reply="Got it. When should we call you back?",
                location="Austin, TX",
                postal_code="10115",
                service_requested="Roof repair",
                description="Leak in kitchen",
                urgency="medium",
                preferred_callback_time="Friday afternoon",
            ),
        ],
    )

    first = await service.handle_message(
        LeadMessageRequest(
            conversation_id="lead-conv-merge",
            message="I'm Jane at 01701234567",
        ),
        company_id=company.id,
    )
    second = await service.handle_message(
        LeadMessageRequest(
            conversation_id="lead-conv-merge",
            message="Roof repair in Austin, leak in kitchen, medium urgency, call Friday afternoon.",
        ),
        company_id=company.id,
    )

    assert first.lead_complete is False
    assert second.lead_complete is True
    assert second.extracted_data.name == "Jane Doe"
    assert second.extracted_data.service_requested == "Roof repair"


@pytest.mark.asyncio
async def test_lead_capture_service_persists_across_service_reinstantiation(
    conversation_repository: ConversationRepository,
    lead_repository,
    company_repository,
    company_activation_repository,
    company,
) -> None:
    first_service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks Jane. What service do you need?",
                name="Jane Doe",
                phone="01701234567",
            ),
        ],
    )
    await first_service.handle_message(
        LeadMessageRequest(
            conversation_id="lead-conv-restart",
            message="I'm Jane at 01701234567",
        ),
        company_id=company.id,
    )

    second_service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Got it. When should we call you back?",
                location="Austin, TX",
                postal_code="10115",
                service_requested="Roof repair",
                description="Leak in kitchen",
                urgency="medium",
                preferred_callback_time="Friday afternoon",
            ),
        ],
    )
    response = await second_service.handle_message(
        LeadMessageRequest(
            conversation_id="lead-conv-restart",
            message="Roof repair in Austin, leak in kitchen, medium urgency, call Friday afternoon.",
        ),
        company_id=company.id,
    )

    assert response.extracted_data.name == "Jane Doe"
    assert response.extracted_data.phone == "01701234567"
    assert response.lead_complete is True

    messages = conversation_repository.list_messages(
        conversation_repository.get_by_external_id(
            company_id=company.id,
            external_id="lead-conv-restart",
        ).id,
    )
    assert len(messages) == 4
    assert messages[0].content == "I'm Jane at 01701234567"
    assert messages[2].content == (
        "Roof repair in Austin, leak in kitchen, medium urgency, call Friday afternoon."
    )


@pytest.mark.asyncio
async def test_lead_capture_service_rejects_invalid_phone_number(
    conversation_repository: ConversationRepository,
    lead_repository,
    company_repository,
    company_activation_repository,
    company,
) -> None:
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        company_activation_repository=company_activation_repository,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Danke, ich habe Ihre Nummer notiert.",
                phone="123",
            ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="lead-conv-invalid-phone",
            message="Meine Nummer ist 123.",
        ),
        company_id=company.id,
    )

    assert response.extracted_data.phone is None
    assert response.contactable is False
    assert "Telefonnummer" in response.reply
    assert "0170" in response.reply

