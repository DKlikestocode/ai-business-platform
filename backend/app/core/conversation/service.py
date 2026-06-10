import json

from app.core.memory.interface import MemoryStore
from app.core.memory.models import ConversationMessage, MessageRole
from app.core.prompts.builder import PromptBuilder
from app.core.llm.models import ChatMessage


class ConversationService:
    """Manages conversation history and prompt assembly."""

    def __init__(
        self,
        memory: MemoryStore,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self._memory = memory
        self._prompt_builder = prompt_builder or PromptBuilder()

    async def get_history(
        self,
        conversation_id: str,
        *,
        limit: int | None = None,
    ) -> list[ConversationMessage]:
        return await self._memory.get_messages(conversation_id, limit=limit)

    async def record_user_message(
        self,
        conversation_id: str,
        content: str,
        *,
        metadata: dict | None = None,
    ) -> ConversationMessage:
        message = ConversationMessage(
            role=MessageRole.USER,
            content=content,
            metadata=metadata or {},
        )
        return await self._memory.append_message(conversation_id, message)

    async def record_assistant_message(
        self,
        conversation_id: str,
        content: str,
        *,
        metadata: dict | None = None,
    ) -> ConversationMessage:
        message = ConversationMessage(
            role=MessageRole.ASSISTANT,
            content=content,
            metadata=metadata or {},
        )
        return await self._memory.append_message(conversation_id, message)

    async def record_tool_result(
        self,
        conversation_id: str,
        *,
        tool_call_id: str,
        tool_name: str,
        output: str,
    ) -> ConversationMessage:
        message = ConversationMessage(
            role=MessageRole.TOOL,
            content=output,
            name=tool_name,
            tool_call_id=tool_call_id,
        )
        return await self._memory.append_message(conversation_id, message)

    async def record_assistant_tool_calls(
        self,
        conversation_id: str,
        *,
        content: str | None,
        tool_calls: list,
    ) -> ConversationMessage:
        message = ConversationMessage(
            role=MessageRole.ASSISTANT,
            content=content or "",
            metadata={"tool_calls": tool_calls},
        )
        return await self._memory.append_message(conversation_id, message)

    async def build_messages(
        self,
        conversation_id: str,
        system_prompt: str,
        *,
        limit: int | None = None,
    ) -> list[ChatMessage]:
        history = await self.get_history(conversation_id, limit=limit)
        return self._prompt_builder.build(system_prompt=system_prompt, history=history)

    async def clear(self, conversation_id: str) -> None:
        await self._memory.clear_conversation(conversation_id)

    @staticmethod
    def serialize_tool_output(payload: object) -> str:
        if isinstance(payload, str):
            return payload
        return json.dumps(payload, default=str)
