import logging

from openai import AsyncOpenAI

from app.agents.lead_agent.extraction import LeadExtractionClient
from app.agents.lead_agent.models import LeadCaptureLLMOutput
from app.core.exceptions import LLMServiceError
from app.core.llm.models import ChatMessage

logger = logging.getLogger(__name__)


class OpenAILeadExtractionClient(LeadExtractionClient):
    """OpenAI structured-output client for lead capture."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str | None = None,
        organization: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self._model = model
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            organization=organization,
            timeout=timeout,
        )

    async def extract(
        self,
        *,
        messages: list[ChatMessage],
    ) -> LeadCaptureLLMOutput:
        payload = [
            {
                "role": message.role,
                "content": message.content or "",
            }
            for message in messages
        ]
        try:
            response = await self._client.beta.chat.completions.parse(
                model=self._model,
                messages=payload,
                response_format=LeadCaptureLLMOutput,
            )
        except Exception as exc:
            logger.exception("Lead extraction failed")
            raise LLMServiceError(str(exc)) from exc

        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise LLMServiceError("Lead extraction returned empty structured output.")
        return parsed
