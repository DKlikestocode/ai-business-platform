from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import LLMServiceError
from app.core.llm.models import ChatCompletionRequest, ChatMessage
from app.core.llm.openai_service import OpenAIService


@pytest.mark.asyncio
async def test_openai_service_maps_response() -> None:
    service = OpenAIService(api_key="test", model="gpt-test")

    mock_message = MagicMock()
    mock_message.content = "Hello"
    mock_message.tool_calls = None

    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_choice.finish_reason = "stop"

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.model = "gpt-test"
    mock_response.usage = MagicMock(
        prompt_tokens=1,
        completion_tokens=2,
        total_tokens=3,
    )
    mock_response.model_dump.return_value = {"id": "chatcmpl-test"}

    with patch.object(
        service._client.chat.completions,
        "create",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await service.chat_completion(
            ChatCompletionRequest(messages=[ChatMessage(role="user", content="Hi")]),
        )

    assert response.content == "Hello"
    assert response.finish_reason == "stop"
    assert response.usage["total_tokens"] == 3


@pytest.mark.asyncio
async def test_openai_service_wraps_provider_errors() -> None:
    service = OpenAIService(api_key="test", model="gpt-test")

    with patch.object(
        service._client.chat.completions,
        "create",
        new=AsyncMock(side_effect=RuntimeError("provider down")),
    ):
        with pytest.raises(LLMServiceError):
            await service.chat_completion(
                ChatCompletionRequest(messages=[ChatMessage(role="user", content="Hi")]),
            )
