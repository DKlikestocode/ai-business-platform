from app.core.llm.models import ChatMessage
from app.core.memory.models import ConversationMessage, MessageRole


class PromptBuilder:
    """Builds LLM-ready message lists from conversation history."""

    def build(
        self,
        *,
        system_prompt: str,
        history: list[ConversationMessage],
        include_system: bool = True,
    ) -> list[ChatMessage]:
        messages: list[ChatMessage] = []
        if include_system and system_prompt.strip():
            messages.append(ChatMessage(role=MessageRole.SYSTEM, content=system_prompt))

        for item in history:
            messages.append(self._from_conversation_message(item))
        return messages

    @staticmethod
    def _from_conversation_message(message: ConversationMessage) -> ChatMessage:
        return ChatMessage(
            role=message.role.value,
            content=message.content,
            name=message.name,
            tool_call_id=message.tool_call_id,
            tool_calls=message.metadata.get("tool_calls", []),
        )
