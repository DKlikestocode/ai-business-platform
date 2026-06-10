from typing import Protocol, runtime_checkable

from app.agents.lead_agent.models import LeadCaptureLLMOutput
from app.core.llm.models import ChatMessage


@runtime_checkable
class LeadExtractionClient(Protocol):
    """Contract for structured lead extraction from conversation context."""

    async def extract(
        self,
        *,
        messages: list[ChatMessage],
    ) -> LeadCaptureLLMOutput:
        """Return a structured reply and extracted lead fields."""
