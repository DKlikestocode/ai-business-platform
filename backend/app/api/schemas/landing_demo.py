from pydantic import BaseModel, Field, field_validator

LANDING_DEMO_CONVERSATION_PREFIX = "landing-demo-"


class LandingDemoMessageRequest(BaseModel):
    conversation_id: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("conversation_id")
    @classmethod
    def validate_conversation_id(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed.startswith(LANDING_DEMO_CONVERSATION_PREFIX):
            raise ValueError("Invalid landing demo conversation id.")
        return trimmed

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Message cannot be empty.")
        if len(trimmed) > 2000:
            raise ValueError("Message cannot exceed 2000 characters.")
        return trimmed
