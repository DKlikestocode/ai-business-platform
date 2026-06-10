from typing import Any

from app.core.memory.interface import MemoryStore
from app.core.memory.models import ConversationMessage, MemoryContext


class InMemoryStore(MemoryStore):
    """In-process memory store for development and testing."""

    def __init__(self) -> None:
        self._messages: dict[str, list[ConversationMessage]] = {}
        self._context: dict[str, dict[str, Any]] = {}

    async def get_messages(
        self,
        conversation_id: str,
        *,
        limit: int | None = None,
    ) -> list[ConversationMessage]:
        messages = list(self._messages.get(conversation_id, []))
        if limit is not None:
            return messages[-limit:]
        return messages

    async def append_message(
        self,
        conversation_id: str,
        message: ConversationMessage,
    ) -> ConversationMessage:
        self._messages.setdefault(conversation_id, []).append(message)
        return message

    async def get_context(self, conversation_id: str) -> MemoryContext:
        return MemoryContext(
            conversation_id=conversation_id,
            data=dict(self._context.get(conversation_id, {})),
        )

    async def update_context(
        self,
        conversation_id: str,
        updates: dict[str, Any],
    ) -> MemoryContext:
        bucket = self._context.setdefault(conversation_id, {})
        bucket.update(updates)
        return MemoryContext(conversation_id=conversation_id, data=dict(bucket))

    async def clear_conversation(self, conversation_id: str) -> None:
        self._messages.pop(conversation_id, None)
        self._context.pop(conversation_id, None)
