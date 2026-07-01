from app.agents.lead_agent.conversation_flow import (
    POSTAL_CODE_NUDGE,
    POSTAL_CODE_REQUEST_REPLY,
    PROBLEM_AND_POSTAL_CODE_FIRST_REPLY,
    PROBLEM_FIRST_REPLY,
    resolve_qualification_reply,
)
from app.agents.lead_agent.models import LeadExtractedData
from app.db.models.enums import ConversationChannel


def test_hallo_gets_problem_first_reply_when_llm_asks_contact() -> None:
    data = LeadExtractedData()

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Bitte nennen Sie Telefon oder E-Mail.",
    )

    assert reply == PROBLEM_FIRST_REPLY
    assert "Telefon" not in reply


def test_hallo_keeps_conversational_llm_reply() -> None:
    data = LeadExtractedData()
    llm_reply = "Guten Tag! Schön, dass Sie sich melden. Wobei können wir Ihnen helfen?"

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply=llm_reply,
    )

    assert reply == llm_reply


def test_hallo_with_service_area_asks_problem_when_llm_asks_contact() -> None:
    data = LeadExtractedData()

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Bitte nennen Sie Telefon oder E-Mail.",
        service_area_configured=True,
    )

    assert reply == PROBLEM_AND_POSTAL_CODE_FIRST_REPLY
    assert "Postleitzahl" in reply


def test_description_without_contact_appends_contact_nudge_to_llm_reply() -> None:
    data = LeadExtractedData(description="Heizung defekt")
    llm_reply = "Das klingt unangenehm. Seit wann ist die Heizung ausgefallen?"

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply=llm_reply,
    )

    assert llm_reply in reply
    assert "Telefon" in reply


def test_description_without_contact_keeps_llm_reply_when_it_asks_contact() -> None:
    data = LeadExtractedData(description="Heizung defekt")
    llm_reply = "Was ist Ihre Telefonnummer?"

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply=llm_reply,
    )

    assert reply == llm_reply


def test_description_without_postal_code_appends_plz_nudge_to_llm_reply() -> None:
    data = LeadExtractedData(description="Heizung defekt")
    llm_reply = "Das klingt unangenehm. Seit wann ist die Heizung ausgefallen?"

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply=llm_reply,
        service_area_configured=True,
    )

    assert llm_reply in reply
    assert POSTAL_CODE_NUDGE in reply


def test_description_without_postal_code_uses_template_when_llm_asks_contact() -> None:
    data = LeadExtractedData(description="Heizung defekt")

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply="Was ist Ihre Telefonnummer?",
        service_area_configured=True,
    )

    assert reply == POSTAL_CODE_REQUEST_REPLY
    assert "Postleitzahl" in reply


def test_description_with_postal_code_keeps_llm_reply_when_it_asks_contact() -> None:
    data = LeadExtractedData(description="Heizung defekt", postal_code="22303")
    llm_reply = "Was ist Ihre Telefonnummer?"

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply=llm_reply,
        service_area_configured=True,
    )

    assert reply == llm_reply


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
