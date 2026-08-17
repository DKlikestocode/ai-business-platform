from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IntakeChannel(StrEnum):
    EMAIL = "email"
    WEBSITE = "website"
    VOICE = "voice"
    WHATSAPP = "whatsapp"
    MANUAL = "manual"


class IntakeStatus(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    READY = "ready"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"
    EXPORTED = "exported"
    DISCARDED = "discarded"


class IntakeUrgency(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class IntakeKind(StrEnum):
    APPOINTMENT_CONSULTATION = "appointment_consultation"
    QUOTE = "quote"
    OTHER = "other"


class IntakeScope(StrEnum):
    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope"
    UNCLEAR = "unclear"


class RecommendedAction(StrEnum):
    CALL_IMMEDIATELY = "call_immediately"
    SCHEDULE_VISIT = "schedule_visit"
    PREPARE_QUOTE = "prepare_quote"
    REQUEST_MISSING_INFORMATION = "request_missing_information"
    MANUAL_ROUTE = "manual_route"
    DISCARD_SPAM = "discard_spam"
    MERGE_DUPLICATE = "merge_duplicate"


class IntakeReviewDecision(StrEnum):
    APPROVE = "approve"
    SAVE_FOR_REVIEW = "save_for_review"
    DISCARD = "discard"


class ServiceAddress(BaseModel):
    model_config = ConfigDict(extra="forbid")

    street: str | None = None
    postal_code: str | None = None
    city: str | None = None


class IntakeFieldConfidence(BaseModel):
    """Closed confidence schema compatible with OpenAI Structured Outputs."""

    model_config = ConfigDict(extra="forbid")

    customer_name: float | None = None
    company: float | None = None
    email: float | None = None
    phone: float | None = None
    service_address: float | None = None
    service_requested: float | None = None
    description: float | None = None
    urgency: float | None = None
    preferred_time: float | None = None
    inquiry_kind: float | None = None
    inquiry_scope: float | None = None
    contactable: float | None = None
    needs_human_review: float | None = None
    recommended_action: float | None = None
    safety_warning: float | None = None
    duplicate_of: float | None = None

    @field_validator("*")
    @classmethod
    def validate_confidence(cls, value: float | None) -> float | None:
        if value is not None and not 0 <= value <= 1:
            raise ValueError("field confidence must be between 0 and 1")
        return value

    def as_dict(self) -> dict[str, float]:
        return self.model_dump(mode="json", exclude_none=True)


class IntakeExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_name: str | None = None
    company: str | None = None
    email: str | None = None
    phone: str | None = None
    service_address: ServiceAddress = Field(default_factory=ServiceAddress)
    service_requested: str | None = None
    description: str | None = None
    urgency: IntakeUrgency = IntakeUrgency.UNKNOWN
    preferred_time: str | None = None
    inquiry_kind: IntakeKind = IntakeKind.OTHER
    inquiry_scope: IntakeScope = IntakeScope.UNCLEAR
    contactable: bool = False
    needs_human_review: bool = True
    review_reasons: list[str] = Field(default_factory=list)
    recommended_action: RecommendedAction = RecommendedAction.MANUAL_ROUTE
    field_confidence: IntakeFieldConfidence = Field(
        default_factory=IntakeFieldConfidence
    )
    safety_warning: str | None = None
    duplicate_of: str | None = None


class ParsedAttachment(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    content: bytes
    sha256: str = Field(min_length=64, max_length=64)

    @property
    def size_bytes(self) -> int:
        return len(self.content)

    @property
    def is_pdf(self) -> bool:
        return self.content_type.lower() == "application/pdf"


class ParsedEmail(BaseModel):
    message_id: str | None = None
    subject: str
    sender_name: str | None = None
    sender_email: str | None = None
    received_at: datetime | None = None
    body_text: str
    attachments: list[ParsedAttachment] = Field(default_factory=list)
