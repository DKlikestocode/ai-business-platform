from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class LeadStatus(StrEnum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    WON = "won"
    LOST = "lost"


class ContactMethod(StrEnum):
    PHONE = "phone"
    EMAIL = "email"
    CHANNEL = "channel"
    UNKNOWN = "unknown"


class QualificationStatus(StrEnum):
    INCOMPLETE = "incomplete"
    CONTACTABLE = "contactable"
    QUALIFIED = "qualified"


InquiryScope = Literal["in_scope", "out_of_scope", "unclear"]


REQUIRED_LEAD_FIELDS: tuple[str, ...] = (
    "name",
    "phone",
    "postal_code",
    "location",
    "service_requested",
    "description",
    "urgency",
    "preferred_callback_time",
)

OPTIONAL_LEAD_FIELDS: tuple[str, ...] = (
    "email",
    "company",
)


class LeadExtractedData(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    company: str | None = None
    location: str | None = None
    postal_code: str | None = None
    service_requested: str | None = None
    description: str | None = None
    urgency: str | None = None
    preferred_callback_time: str | None = None


class LeadCaptureLLMOutput(BaseModel):
    reply: str = Field(description="Natural conversational reply to the customer.")
    summary: str | None = Field(
        default=None,
        description="Short lead summary once enough information is available.",
    )
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    company: str | None = None
    location: str | None = None
    postal_code: str | None = None
    service_requested: str | None = None
    description: str | None = None
    urgency: str | None = Field(
        default=None,
        description=(
            "Dringlichkeit als genau einer von: hoch, mittel, niedrig. "
            "heute/sofort/Notfall → hoch; morgen/bald/diese Woche → mittel; "
            "keine Eile/flexibel → niedrig."
        ),
    )
    preferred_callback_time: str | None = Field(
        default=None,
        description=(
            "Gewünschte Zeit in den Worten des Kunden für Termin/Besuch/Einsatz vor Ort "
            "oder telefonischen Rückruf — z. B. nächsten Montag, heute Nachmittag, morgen früh. "
            "Bei Wasserschaden/Reparatur meist Termin vor Ort, nicht nur Rückruf."
        ),
    )
    inquiry_scope: InquiryScope | None = Field(
        default=None,
        description=(
            "Passt das Anliegen zum Leistungsspektrum des Betriebs? "
            "in_scope = konkretes Anliegen im Spektrum; "
            "out_of_scope = klar anderer Bereich/Gewerk; "
            "unclear = noch unklar, kurze Rückfrage nötig. "
            "Nur setzen, wenn ein Branchen-Kontext im Prompt steht."
        ),
    )

    def to_extracted_data(self) -> LeadExtractedData:
        return LeadExtractedData(
            name=self.name,
            phone=self.phone,
            email=self.email,
            company=self.company,
            location=self.location,
            postal_code=self.postal_code,
            service_requested=self.service_requested,
            description=self.description,
            urgency=self.urgency,
            preferred_callback_time=self.preferred_callback_time,
        )


class LeadCaptureResult(BaseModel):
    reply: str
    lead_complete: bool
    missing_fields: list[str]
    extracted_data: LeadExtractedData
    lead_id: str | None = None
    summary: str | None = None
    contactable: bool = False
    contact_method: ContactMethod = ContactMethod.UNKNOWN
    lead_score: int = 0
    qualification_status: QualificationStatus = QualificationStatus.INCOMPLETE


class LeadMessageRequest(BaseModel):
    conversation_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class LeadMessageResponse(BaseModel):
    reply: str
    lead_complete: bool
    missing_fields: list[str]
    extracted_data: LeadExtractedData
    lead_id: str | None = None
    contactable: bool = False
    contact_method: ContactMethod = ContactMethod.UNKNOWN
    lead_score: int = 0
    qualification_status: QualificationStatus = QualificationStatus.INCOMPLETE
