from app.agents.lead_agent.conversation_flow import (
    CONTACT_REQUEST_REPLY,
    POSTAL_CODE_REQUEST_REPLY,
    PROBLEM_AND_POSTAL_CODE_FIRST_REPLY,
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


def test_hallo_with_service_area_asks_problem_and_postal_code() -> None:
    data = LeadExtractedData()

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Bitte nennen Sie Telefon oder E-Mail.",
        service_area_configured=True,
    )

    assert reply == PROBLEM_AND_POSTAL_CODE_FIRST_REPLY
    assert "Postleitzahl" in reply
    assert "Einsatzgebiet" in reply


def test_description_without_contact_gets_contact_reply() -> None:
    data = LeadExtractedData(description="Heizung defekt")

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Was ist Ihre Telefonnummer?",
    )

    assert reply == CONTACT_REQUEST_REPLY


def test_description_without_postal_code_and_service_area_gets_plz_reply() -> None:
    data = LeadExtractedData(description="Heizung defekt")

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Was ist Ihre Telefonnummer?",
        service_area_configured=True,
    )

    assert reply == POSTAL_CODE_REQUEST_REPLY
    assert "Einsatzgebiet" in reply


def test_description_with_postal_code_gets_contact_reply_when_service_area() -> None:
    data = LeadExtractedData(description="Heizung defekt", postal_code="22303")

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Was ist Ihre Telefonnummer?",
        service_area_configured=True,
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
