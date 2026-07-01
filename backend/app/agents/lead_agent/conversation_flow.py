"""Minimal reply fallbacks for website lead capture — LLM replies are preferred."""

from app.agents.lead_agent.models import LeadExtractedData
from app.db.models.enums import ConversationChannel

PROBLEM_FIRST_REPLY = (
    "Guten Tag! Wobei können wir Ihnen helfen? "
    "Beschreiben Sie bitte kurz Ihr Anliegen oder das Problem."
)

PROBLEM_AND_POSTAL_CODE_FIRST_REPLY = (
    "Guten Tag! Wobei können wir Ihnen helfen? "
    "Beschreiben Sie bitte kurz Ihr Anliegen — und wenn möglich gleich mit Ihrer Postleitzahl, "
    "damit wir einschätzen können, ob wir bei Ihnen vor Ort sind."
)

_WEB_CHANNELS = {ConversationChannel.WEB, ConversationChannel.LANDING_DEMO}


def resolve_qualification_reply(
    *,
    merged_data: LeadExtractedData,
    channel: ConversationChannel,
    llm_reply: str,
    service_area_configured: bool = False,
) -> str:
    """Use the LLM reply; only fall back when the model returns nothing."""
    del merged_data
    if channel not in _WEB_CHANNELS:
        return llm_reply

    reply = (llm_reply or "").strip()
    if reply:
        return reply

    if service_area_configured and channel == ConversationChannel.WEB:
        return PROBLEM_AND_POSTAL_CODE_FIRST_REPLY
    return PROBLEM_FIRST_REPLY
