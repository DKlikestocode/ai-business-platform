from uuid import UUID

from app.config import Settings
from app.repositories.conversation_repository import ConversationRepository


class LandingDemoLimitError(Exception):
    """Raised when a landing demo conversation exceeds the message limit."""


def ensure_landing_demo_message_allowed(
    *,
    conversation_repository: ConversationRepository,
    company_id: UUID,
    conversation_external_id: str,
    settings: Settings,
) -> None:
    conversation = conversation_repository.get_by_external_id(
        company_id=company_id,
        external_id=conversation_external_id,
    )
    if conversation is None:
        return

    user_messages = conversation_repository.count_user_messages(conversation.id)
    if user_messages >= settings.landing_demo_max_user_messages:
        raise LandingDemoLimitError()
