from dataclasses import dataclass

from app.agents.lead_agent.contact_validation import is_valid_email, is_valid_phone
from app.agents.lead_agent.models import ContactMethod, LeadExtractedData, QualificationStatus
from app.agents.lead_agent.utils import is_lead_complete
from app.db.models.enums import ConversationChannel
from app.services.service_area.evaluate import resolve_lead_postal_code


@dataclass(frozen=True)
class QualificationResult:
    contactable: bool
    contact_method: ContactMethod
    lead_score: int
    qualification_status: QualificationStatus

    @property
    def is_qualified(self) -> bool:
        return self.qualification_status == QualificationStatus.QUALIFIED

    @property
    def should_persist(self) -> bool:
        return self.qualification_status in {
            QualificationStatus.CONTACTABLE,
            QualificationStatus.QUALIFIED,
        }


def _has_value(value: str | None) -> bool:
    return value is not None and bool(str(value).strip())


def _has_contact_phone(data: LeadExtractedData) -> bool:
    return is_valid_phone(data.phone)


def _has_contact_email(data: LeadExtractedData) -> bool:
    return is_valid_email(data.email)


def has_contact_method(
    data: LeadExtractedData,
    *,
    channel: ConversationChannel,
) -> bool:
    return (
        _has_contact_phone(data)
        or _has_contact_email(data)
        or channel in {ConversationChannel.WHATSAPP, ConversationChannel.VOICE}
    )


def resolve_contact_method(
    data: LeadExtractedData,
    *,
    channel: ConversationChannel,
) -> ContactMethod:
    if channel == ConversationChannel.WHATSAPP:
        return ContactMethod.CHANNEL
    if channel == ConversationChannel.VOICE:
        if _has_contact_phone(data):
            return ContactMethod.PHONE
        return ContactMethod.CHANNEL
    if _has_contact_phone(data):
        return ContactMethod.PHONE
    if _has_contact_email(data):
        return ContactMethod.EMAIL
    return ContactMethod.UNKNOWN


def calculate_lead_score(
    data: LeadExtractedData,
    *,
    channel: ConversationChannel,
) -> int:
    score = 0
    if has_contact_method(data, channel=channel):
        score += 25
    if _has_value(data.description):
        score += 20
    if _has_value(data.location):
        score += 10
    if _has_value(data.postal_code):
        score += 5
    if _has_value(data.service_requested):
        score += 15
    if _has_value(data.urgency):
        score += 10
    if _has_value(data.name):
        score += 10
    if _has_value(data.preferred_callback_time):
        score += 5
    return min(score, 100)


def has_useful_context(data: LeadExtractedData) -> bool:
    return (
        _has_value(data.description)
        or _has_value(data.service_requested)
        or _has_value(data.location)
        or _has_value(data.postal_code)
    )


def evaluate_qualification(
    data: LeadExtractedData,
    *,
    channel: ConversationChannel,
) -> QualificationResult:
    contactable = has_contact_method(data, channel=channel)
    contact_method = resolve_contact_method(data, channel=channel)
    lead_score = calculate_lead_score(data, channel=channel)

    if is_lead_complete(data):
        status = QualificationStatus.QUALIFIED
    elif not contactable or not has_useful_context(data):
        status = QualificationStatus.INCOMPLETE
    else:
        status = QualificationStatus.CONTACTABLE

    return QualificationResult(
        contactable=contactable,
        contact_method=contact_method,
        lead_score=lead_score,
        qualification_status=status,
    )


def build_qualification_hint(
    data: LeadExtractedData,
    qualification: QualificationResult,
    *,
    channel: ConversationChannel,
    service_area_configured: bool = False,
) -> str:
    if qualification.qualification_status == QualificationStatus.QUALIFIED:
        return (
            "All required business fields are collected. Confirm receipt, next steps, "
            "and expected callback timing. Do not ask unnecessary repeated questions."
        )

    if not has_useful_context(data):
        return (
            "The customer's request is not clear yet. Respond naturally to their message, "
            "then ask one focused question about what they need help with. Do not ask for "
            "phone or email before the problem or service is understood."
        )

    if (
        service_area_configured
        and channel == ConversationChannel.WEB
        and resolve_lead_postal_code(data) is None
    ):
        return (
            "The request is understood. Acknowledge what the customer shared, then ask for "
            "their 5-digit German postal code to check service area coverage. Keep the tone "
            "conversational — do not ignore their message or jump straight to contact details."
        )

    if not qualification.contactable:
        return (
            "The request is understood, but no reliable contact method is available yet. "
            "Ask for a phone number or email so the business can follow up. If the customer "
            "provided an invalid phone number or email, ask again and give a short example format."
        )

    if not _has_value(data.description) and not _has_value(data.service_requested):
        return (
            "A contact method is available, but the problem or service is still unclear. "
            "Ask for a concise description of the issue or service needed."
        )

    if qualification.qualification_status == QualificationStatus.CONTACTABLE:
        return (
            "The lead is contactable with useful context. Confirm the request was received "
            "and only ask for missing high-value details."
        )

    if channel == ConversationChannel.WHATSAPP:
        return (
            "This conversation is on WhatsApp. Treat the channel as the contact method and "
            "focus on gathering useful service context."
        )

    if channel == ConversationChannel.VOICE:
        return (
            "This is a phone call. Keep replies short and spoken-friendly. The caller is "
            "reachable by phone — confirm callback number only if it may differ from caller "
            "ID. Prioritize problem, location or postal code, and urgency."
        )

    return "Continue qualifying the lead with one or two focused questions at a time."
