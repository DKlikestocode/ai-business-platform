import pytest

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadExtractedData, QualificationStatus
from app.agents.lead_agent.qualification import (
    build_qualification_hint,
    evaluate_qualification,
)
from app.core.agent_engine.context import AgentContext
from app.db.models.enums import ConversationChannel


def test_whatsapp_channel_counts_as_contactable() -> None:
    data = LeadExtractedData(urgency="high")

    qualification = evaluate_qualification(data, channel=ConversationChannel.WHATSAPP)

    assert qualification.contactable is True
    assert qualification.contact_method.value == "channel"


def test_non_contactable_message_is_incomplete() -> None:
    data = LeadExtractedData(urgency="high", description="Need help urgently")

    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)

    assert qualification.contactable is False
    assert qualification.qualification_status == QualificationStatus.INCOMPLETE
    assert qualification.lead_score == 30


def test_contactable_partial_lead_scores_above_threshold() -> None:
    data = LeadExtractedData(
        phone="01701234567",
        description="Roof is leaking",
        location="Berlin",
    )

    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)

    assert qualification.contactable is True
    assert qualification.qualification_status == QualificationStatus.CONTACTABLE
    assert qualification.lead_score == 55


def test_contactable_low_score_stays_incomplete_without_context() -> None:
    data = LeadExtractedData(phone="01701234567")

    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)

    assert qualification.contactable is True
    assert qualification.qualification_status == QualificationStatus.INCOMPLETE
    assert qualification.lead_score == 25


def test_complete_lead_is_qualified() -> None:
    data = LeadExtractedData(
        name="Jane Doe",
        phone="01701234567",
        location="Berlin",
        postal_code="10115",
        service_requested="Roof repair",
        description="Leak in kitchen",
        urgency="high",
        preferred_callback_time="Tomorrow morning",
    )

    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)

    assert qualification.qualification_status == QualificationStatus.QUALIFIED
    assert qualification.lead_score == 100


@pytest.mark.asyncio
async def test_agent_prioritizes_problem_context_when_missing() -> None:
    agent = LeadCaptureAgent()
    data = LeadExtractedData(urgency="high")
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)
    context = AgentContext(
        conversation_id="conv-1",
        agent_name=agent.name,
        metadata={
            "qualification_hint": build_qualification_hint(
                data,
                qualification,
                channel=ConversationChannel.WEB,
            ),
        },
    )

    prompt = await agent.build_system_prompt(context)

    assert "problem" in prompt.lower() or "service" in prompt.lower()
    hint = context.metadata["qualification_hint"].lower()
    assert "phone" not in hint or "before" in hint


def test_qualification_hint_prioritizes_problem_before_contact() -> None:
    data = LeadExtractedData()
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)

    hint = build_qualification_hint(data, qualification, channel=ConversationChannel.WEB)

    assert "problem" in hint.lower() or "service" in hint.lower()
    assert "contact method" not in hint.lower() or "understood" in hint.lower()


def test_qualification_hint_asks_postal_code_when_service_area_configured() -> None:
    data = LeadExtractedData(description="Heizung defekt")
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)

    hint = build_qualification_hint(
        data,
        qualification,
        channel=ConversationChannel.WEB,
        service_area_configured=True,
    )

    assert "postal code" in hint.lower()
    assert "conversational" in hint.lower()


def test_qualification_hint_asks_contact_after_context() -> None:
    data = LeadExtractedData(description="Heizung defekt")
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)

    hint = build_qualification_hint(data, qualification, channel=ConversationChannel.WEB)

    assert "phone" in hint.lower() or "email" in hint.lower()
