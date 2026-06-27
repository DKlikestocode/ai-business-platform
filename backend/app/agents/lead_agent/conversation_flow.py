"""Deterministic reply ordering for website lead capture."""

from app.agents.lead_agent.models import LeadExtractedData
from app.agents.lead_agent.qualification import has_contact_method, has_useful_context
from app.db.models.enums import ConversationChannel

PROBLEM_FIRST_REPLY = (
    "Guten Tag! Wobei können wir Ihnen helfen? "
    "Beschreiben Sie bitte kurz Ihr Anliegen oder das Problem."
)

CONTACT_REQUEST_REPLY = (
    "Vielen Dank für die Schilderung. Damit wir uns bei Ihnen melden können, "
    "benötigen wir noch Ihre Telefonnummer oder E-Mail-Adresse."
)

_WEB_CHANNELS = {ConversationChannel.WEB, ConversationChannel.LANDING_DEMO}


def resolve_qualification_reply(
    *,
    merged_data: LeadExtractedData,
    channel: ConversationChannel,
    llm_reply: str,
) -> str:
    """Enforce problem-before-contact on website channels."""
    if channel not in _WEB_CHANNELS:
        return llm_reply
    if not has_useful_context(merged_data):
        return PROBLEM_FIRST_REPLY
    if not has_contact_method(merged_data, channel=channel):
        return CONTACT_REQUEST_REPLY
    return llm_reply
