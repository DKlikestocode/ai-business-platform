from dataclasses import dataclass

from app.agents.lead_agent.models import ContactMethod, LeadExtractedData, QualificationStatus
from app.agents.lead_agent.utils import is_lead_complete
from app.db.models.enums import ConversationChannel


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


def has_contact_method(
    data: LeadExtractedData,
    *,
    channel: ConversationChannel,
) -> bool:
    return (
        _has_value(data.phone)
        or _has_value(data.email)
        or channel == ConversationChannel.WHATSAPP
    )


def resolve_contact_method(
    data: LeadExtractedData,
    *,
    channel: ConversationChannel,
) -> ContactMethod:
    if channel == ConversationChannel.WHATSAPP:
        return ContactMethod.CHANNEL
    if _has_value(data.phone):
        return ContactMethod.PHONE
    if _has_value(data.email):
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
        score += 15
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
) -> str:
    if qualification.qualification_status == QualificationStatus.QUALIFIED:
        return (
            "All required business fields are collected. Confirm receipt, next steps, "
            "and expected callback timing. Do not ask unnecessary repeated questions."
        )

    if not qualification.contactable:
        return (
            "No reliable contact method is available yet. Prioritize asking for a phone "
            "number or email before collecting other details."
        )

    if not _has_value(data.description):
        return (
            "A contact method is available, but the problem description is still weak. "
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

    return "Continue qualifying the lead with one or two focused questions at a time."
