"""Deterministic reply ordering for website lead capture."""

from app.agents.lead_agent.models import LeadExtractedData
from app.agents.lead_agent.qualification import has_contact_method, has_useful_context
from app.db.models.enums import ConversationChannel
from app.services.service_area.evaluate import resolve_lead_postal_code

PROBLEM_FIRST_REPLY = (
    "Guten Tag! Wobei können wir Ihnen helfen? "
    "Beschreiben Sie bitte kurz Ihr Anliegen oder das Problem."
)

PROBLEM_AND_POSTAL_CODE_FIRST_REPLY = (
    "Guten Tag! Wobei können wir Ihnen helfen? "
    "Beschreiben Sie bitte kurz Ihr Anliegen und nennen Sie Ihre Postleitzahl. "
    "Anhand der PLZ können wir einschätzen, ob Sie in unserem Einsatzgebiet liegen."
)

POSTAL_CODE_REQUEST_REPLY = (
    "Vielen Dank für die Schilderung. Damit wir einschätzen können, ob Sie in "
    "unserem Einsatzgebiet liegen, benötigen wir noch Ihre 5-stellige Postleitzahl."
)

CONTACT_REQUEST_REPLY = (
    "Vielen Dank für die Schilderung. Damit wir uns bei Ihnen melden können, "
    "benötigen wir noch Ihre Telefonnummer oder E-Mail-Adresse."
)

_WEB_CHANNELS = {ConversationChannel.WEB, ConversationChannel.LANDING_DEMO}


def _has_postal_code(data: LeadExtractedData) -> bool:
    return resolve_lead_postal_code(data) is not None


def resolve_qualification_reply(
    *,
    merged_data: LeadExtractedData,
    channel: ConversationChannel,
    llm_reply: str,
    service_area_configured: bool = False,
) -> str:
    """Enforce problem → postal code (if service area) → contact on website channels."""
    if channel not in _WEB_CHANNELS:
        return llm_reply
    if not has_useful_context(merged_data):
        if service_area_configured and channel == ConversationChannel.WEB:
            return PROBLEM_AND_POSTAL_CODE_FIRST_REPLY
        return PROBLEM_FIRST_REPLY
    if (
        service_area_configured
        and channel == ConversationChannel.WEB
        and not _has_postal_code(merged_data)
    ):
        return POSTAL_CODE_REQUEST_REPLY
    if not has_contact_method(merged_data, channel=channel):
        return CONTACT_REQUEST_REPLY
    return llm_reply
