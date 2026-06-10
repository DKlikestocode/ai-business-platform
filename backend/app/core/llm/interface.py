from typing import Protocol, runtime_checkable

from app.core.llm.models import ChatCompletionRequest, ChatCompletionResponse


@runtime_checkable
class LLMService(Protocol):
    """Contract for LLM providers."""

    async def chat_completion(
        self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        """Generate a chat completion response."""
