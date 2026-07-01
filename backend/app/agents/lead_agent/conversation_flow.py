"""Deterministic reply guardrails for website lead capture."""

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
    "Beschreiben Sie bitte kurz Ihr Anliegen — und wenn möglich gleich mit Ihrer Postleitzahl, "
    "damit wir einschätzen können, ob wir bei Ihnen vor Ort sind."
)

POSTAL_CODE_REQUEST_REPLY = (
    "Vielen Dank für die Schilderung — das nehmen wir uns an. "
    "Damit wir prüfen können, ob wir bei Ihnen vor Ort sind: Wie lautet Ihre Postleitzahl?"
)

CONTACT_REQUEST_REPLY = (
    "Vielen Dank für die Schilderung. Damit wir uns bei Ihnen melden können, "
    "benötigen wir noch Ihre Telefonnummer oder E-Mail-Adresse."
)

POSTAL_CODE_NUDGE = "Wie lautet Ihre Postleitzahl?"
CONTACT_NUDGE = (
    "Damit wir uns melden können: Wie erreichen wir Sie am besten — Telefon oder E-Mail?"
)

_CONTACT_MARKERS = ("telefon", "e-mail", "email", "mail@", "erreichen sie", "rufnummer")
_PLZ_MARKERS = ("postleitzahl", "plz")
_PROBLEM_MARKERS = (
    "anliegen",
    "problem",
    "beschreiben",
    "worum",
    "wobei",
    "helfen",
    "service",
    "was ist passiert",
    "was genau",
    "schildern",
)

_WEB_CHANNELS = {ConversationChannel.WEB, ConversationChannel.LANDING_DEMO}


def _has_postal_code(data: LeadExtractedData) -> bool:
    return resolve_lead_postal_code(data) is not None


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def _is_empty_reply(reply: str) -> bool:
    return not reply.strip()


def _append_nudge(reply: str, nudge: str) -> str:
    if nudge.lower() in reply.lower():
        return reply
    return f"{reply.rstrip()}\n\n{nudge}"


def resolve_qualification_reply(
    *,
    merged_data: LeadExtractedData,
    channel: ConversationChannel,
    llm_reply: str,
    service_area_configured: bool = False,
) -> str:
    """Keep conversational LLM replies; enforce order only when the model goes off-track."""
    if channel not in _WEB_CHANNELS:
        return llm_reply

    reply = (llm_reply or "").strip()

    if not has_useful_context(merged_data):
        if _is_empty_reply(reply):
            if service_area_configured and channel == ConversationChannel.WEB:
                return PROBLEM_AND_POSTAL_CODE_FIRST_REPLY
            return PROBLEM_FIRST_REPLY
        if _contains_any(reply, _CONTACT_MARKERS) and not _contains_any(
            reply,
            _PROBLEM_MARKERS,
        ):
            if service_area_configured and channel == ConversationChannel.WEB:
                return PROBLEM_AND_POSTAL_CODE_FIRST_REPLY
            return PROBLEM_FIRST_REPLY
        return reply

    if (
        service_area_configured
        and channel == ConversationChannel.WEB
        and not _has_postal_code(merged_data)
    ):
        if _is_empty_reply(reply):
            return POSTAL_CODE_REQUEST_REPLY
        if _contains_any(reply, _CONTACT_MARKERS) and not _contains_any(
            reply,
            _PLZ_MARKERS,
        ):
            return POSTAL_CODE_REQUEST_REPLY
        if not _contains_any(reply, _PLZ_MARKERS):
            return _append_nudge(reply, POSTAL_CODE_NUDGE)
        return reply

    if not has_contact_method(merged_data, channel=channel):
        if _is_empty_reply(reply):
            return CONTACT_REQUEST_REPLY
        if not _contains_any(reply, _CONTACT_MARKERS):
            return _append_nudge(reply, CONTACT_NUDGE)
        return reply

    return reply
