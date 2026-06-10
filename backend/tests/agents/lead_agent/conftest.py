from app.agents.lead_agent.models import LeadCaptureLLMOutput
from app.core.llm.models import ChatMessage


class MockLeadExtractionClient:
    def __init__(self, outputs: list[LeadCaptureLLMOutput]) -> None:
        self._outputs = list(outputs)
        self.requests: list[list[ChatMessage]] = []

    async def extract(self, *, messages: list[ChatMessage]) -> LeadCaptureLLMOutput:
        self.requests.append(messages)
        if not self._outputs:
            raise RuntimeError("No mock extraction outputs left.")
        return self._outputs.pop(0)
