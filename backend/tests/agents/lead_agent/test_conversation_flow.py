from app.agents.lead_agent.conversation_flow import (
    CONTACT_REQUEST_REPLY,
    PROBLEM_FIRST_REPLY,
    resolve_qualification_reply,
)
from app.agents.lead_agent.models import LeadExtractedData
from app.db.models.enums import ConversationChannel


def test_hallo_gets_problem_first_reply() -> None:
    data = LeadExtractedData()

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Bitte nennen Sie Telefon oder E-Mail.",
    )

    assert reply == PROBLEM_FIRST_REPLY
    assert "Telefon" not in reply


def test_description_without_contact_gets_contact_reply() -> None:
    data = LeadExtractedData(description="Heizung defekt")

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Was ist Ihre Telefonnummer?",
    )

    assert reply == CONTACT_REQUEST_REPLY


def test_contact_and_context_uses_llm_reply() -> None:
    data = LeadExtractedData(
        description="Heizung defekt",
        phone="01701234567",
    )

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Wie dringend ist der Einsatz?",
    )

    assert reply == "Wie dringend ist der Einsatz?"
