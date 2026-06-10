from typing import Any, Protocol, runtime_checkable

from app.core.memory.models import ConversationMessage, MemoryContext


@runtime_checkable
class MemoryStore(Protocol):
    """Persistence contract for conversation history and contextual memory."""

    async def get_messages(
        self,
        conversation_id: str,
        *,
        limit: int | None = None,
    ) -> list[ConversationMessage]:
        """Return conversation messages ordered oldest to newest."""

    async def append_message(
        self,
        conversation_id: str,
        message: ConversationMessage,
    ) -> ConversationMessage:
        """Persist a message and return the stored record."""

    async def get_context(self, conversation_id: str) -> MemoryContext:
        """Return contextual key-value data for a conversation."""

    async def update_context(
        self,
        conversation_id: str,
        updates: dict[str, Any],
    ) -> MemoryContext:
        """Merge contextual updates for a conversation."""

    async def clear_conversation(self, conversation_id: str) -> None:
        """Remove all messages and context for a conversation."""
