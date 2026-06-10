import json
import logging
from typing import Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageToolCall

from app.core.exceptions import LLMServiceError
from app.core.llm.interface import LLMService
from app.core.llm.models import ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from app.core.tools.models import ToolCall, ToolDefinition

logger = logging.getLogger(__name__)


class OpenAIService(LLMService):
    """OpenAI-backed LLM service abstraction."""

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

    async def chat_completion(
        self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        payload = self._build_payload(request)
        try:
            response = await self._client.chat.completions.create(**payload)
        except Exception as exc:
            logger.exception("OpenAI chat completion failed")
            raise LLMServiceError(str(exc)) from exc

        choice = response.choices[0]
        message = choice.message
        tool_calls = self._parse_tool_calls(message.tool_calls)

        usage: dict[str, int] = {}
        if response.usage is not None:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return ChatCompletionResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            model=response.model,
            usage=usage,
            raw=response.model_dump(),
        )

    def _build_payload(self, request: ChatCompletionRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model or self._model,
            "messages": [self._serialize_message(message) for message in request.messages],
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.tools:
            payload["tools"] = [self._serialize_tool(tool) for tool in request.tools]
            payload["tool_choice"] = "auto"
        return payload

    @staticmethod
    def _serialize_message(message: ChatMessage) -> dict[str, Any]:
        data: dict[str, Any] = {"role": message.role}
        if message.content is not None:
            data["content"] = message.content
        if message.name is not None:
            data["name"] = message.name
        if message.tool_call_id is not None:
            data["tool_call_id"] = message.tool_call_id
        if message.tool_calls:
            data["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.name,
                        "arguments": json.dumps(tool_call.arguments),
                    },
                }
                for tool_call in message.tool_calls
            ]
        return data

    @staticmethod
    def _serialize_tool(tool: ToolDefinition) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters.model_dump(by_alias=True),
            },
        }

    @staticmethod
    def _parse_tool_calls(
        tool_calls: list[ChatCompletionMessageToolCall] | None,
    ) -> list[ToolCall]:
        if not tool_calls:
            return []

        parsed: list[ToolCall] = []
        for tool_call in tool_calls:
            arguments_raw = tool_call.function.arguments or "{}"
            try:
                arguments = json.loads(arguments_raw)
            except json.JSONDecodeError:
                arguments = {"raw": arguments_raw}
            parsed.append(
                ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=arguments if isinstance(arguments, dict) else {"value": arguments},
                )
            )
        return parsed
