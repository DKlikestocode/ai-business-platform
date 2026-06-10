import pytest

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput, LeadMessageRequest
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
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
    outputs: list[LeadCaptureLLMOutput],
) -> LeadCaptureService:
    return LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=conversation_repository,
        extraction_client=MockLeadExtractionClient(outputs),
        repository=lead_repository,
        company_repository=company_repository,
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
    )


@pytest.mark.asyncio
async def test_lead_capture_service_tracks_missing_fields(
    conversation_repository: ConversationRepository,
    lead_repository,
    company_repository,
    company,
) -> None:
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        outputs=[
                LeadCaptureLLMOutput(
                    reply="Thanks! What service do you need?",
                    name="Jane Doe",
                    phone="555-0100",
                ),
        ],
    )

    response = await service.handle_message(
        LeadMessageRequest(
            conversation_id="lead-conv-1",
            message="Hi, I'm Jane Doe at 555-0100 in Austin.",
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
    company,
) -> None:
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks, we have everything we need.",
                summary="Jane needs HVAC repair urgently.",
                name="Jane Doe",
                phone="555-0100",
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
    company,
) -> None:
    service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks Jane. What service do you need?",
                name="Jane Doe",
                phone="555-0100",
            ),
            LeadCaptureLLMOutput(
                reply="Got it. When should we call you back?",
                location="Austin, TX",
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
            message="I'm Jane at 555-0100",
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
    company,
) -> None:
    first_service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Thanks Jane. What service do you need?",
                name="Jane Doe",
                phone="555-0100",
            ),
        ],
    )
    await first_service.handle_message(
        LeadMessageRequest(
            conversation_id="lead-conv-restart",
            message="I'm Jane at 555-0100",
        ),
        company_id=company.id,
    )

    second_service = build_service(
        conversation_repository=conversation_repository,
        lead_repository=lead_repository,
        company_repository=company_repository,
        outputs=[
            LeadCaptureLLMOutput(
                reply="Got it. When should we call you back?",
                location="Austin, TX",
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
    assert response.extracted_data.phone == "555-0100"
    assert response.lead_complete is True

    messages = conversation_repository.list_messages(
        conversation_repository.get_by_external_id(
            company_id=company.id,
            external_id="lead-conv-restart",
        ).id,
    )
    assert len(messages) == 4
    assert messages[0].content == "I'm Jane at 555-0100"
    assert messages[2].content == (
        "Roof repair in Austin, leak in kitchen, medium urgency, call Friday afternoon."
    )
