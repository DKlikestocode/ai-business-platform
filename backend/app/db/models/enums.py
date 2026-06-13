from enum import StrEnum


class UserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class ActivationStatus(StrEnum):
    SETUP_INCOMPLETE = "setup_incomplete"
    AWAITING_WIDGET = "awaiting_widget"
    LIVE = "live"
    STALE = "stale"


class ConversationChannel(StrEnum):
    WEB = "web"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    API = "api"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
