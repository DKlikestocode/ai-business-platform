from app.agents.lead_agent.conversation_flow import (
    PROBLEM_AND_POSTAL_CODE_FIRST_REPLY,
    PROBLEM_FIRST_REPLY,
    resolve_qualification_reply,
)
from app.agents.lead_agent.models import LeadExtractedData
from app.db.models.enums import ConversationChannel


def test_empty_llm_reply_uses_problem_first_fallback() -> None:
    reply = resolve_qualification_reply(
        merged_data=LeadExtractedData(),
        channel=ConversationChannel.WEB,
        llm_reply="",
    )
    assert reply == PROBLEM_FIRST_REPLY


def test_empty_llm_reply_with_service_area_uses_combined_fallback() -> None:
    reply = resolve_qualification_reply(
        merged_data=LeadExtractedData(),
        channel=ConversationChannel.WEB,
        llm_reply="   ",
        service_area_configured=True,
    )
    assert reply == PROBLEM_AND_POSTAL_CODE_FIRST_REPLY


def test_substantive_llm_reply_is_kept_even_when_contact_asked_early() -> None:
    data = LeadExtractedData()
    llm_reply = "Bitte nennen Sie Telefon oder E-Mail."

    reply = resolve_qualification_reply(
        merged_data=data,
        channel=ConversationChannel.WEB,
        llm_reply=llm_reply,
        service_area_configured=True,
    )

    assert reply == llm_reply


def test_substantive_llm_reply_kept_without_postal_code_nudge() -> None:
    data = LeadExtractedData(description="Heizung defekt")
    llm_reply = (
        "Vielen Dank, Ihre Postleitzahl 22041 liegt in unserem Einsatzgebiet. "
        "Darf ich bitte noch Ihren Namen und eine Telefonnummer erfahren?"
    )

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
