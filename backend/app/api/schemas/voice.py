from pydantic import BaseModel, Field, field_validator


class VoiceMessageRequest(BaseModel):
    company_slug: str = Field(min_length=1, max_length=255)
    conversation_id: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1, max_length=2000)
    caller_phone: str | None = Field(default=None, max_length=64)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Message cannot be empty.")
        if len(trimmed) > 2000:
            raise ValueError("Message cannot exceed 2000 characters.")
        return trimmed

    @field_validator("caller_phone")
    @classmethod
    def validate_caller_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None


class VoiceMessageResponse(BaseModel):
    reply: str


class TestVoiceIntakeResponse(BaseModel):
    reply: str
    lead_id: str | None = None
