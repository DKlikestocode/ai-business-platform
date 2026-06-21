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
    assert qualification.lead_score == 60


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
        service_requested="Roof repair",
        description="Leak in kitchen",
        urgency="high",
        preferred_callback_time="Tomorrow morning",
    )

    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)

    assert qualification.qualification_status == QualificationStatus.QUALIFIED
    assert qualification.lead_score == 100


@pytest.mark.asyncio
async def test_agent_prioritizes_contact_method_when_missing() -> None:
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

    assert "phone" in prompt.lower()
    assert "email" in prompt.lower()
