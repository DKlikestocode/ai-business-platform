import pytest

from app.core.agent_engine.context import AgentRunRequest
from app.core.exceptions import AgentMaxIterationsError
from app.core.llm.models import ChatCompletionResponse, ToolCall
from tests.conftest import MockLLMService, build_runtime


@pytest.mark.asyncio
async def test_agent_runtime_returns_direct_response(
    conversation_service,
    tool_registry,
    tool_executor,
    test_agent,
) -> None:
    llm = MockLLMService(
        [
            ChatCompletionResponse(content="Done.", finish_reason="stop"),
        ]
    )
    runtime = build_runtime(
        conversation_service,
        tool_registry,
        tool_executor,
        llm,
    )

    result = await runtime.execute(
        test_agent,
        AgentRunRequest(conversation_id="conv-1", input="Run task"),
    )

    assert result.output == "Done."
    assert result.iterations == 1
    assert result.agent_name == "test-agent"
    assert len(result.messages) == 2


@pytest.mark.asyncio
async def test_agent_runtime_executes_tools_before_final_response(
    conversation_service,
    tool_registry,
    tool_executor,
    test_agent,
) -> None:
    llm = MockLLMService(
        [
            ChatCompletionResponse(
                content=None,
                tool_calls=[
                    ToolCall(id="tc-1", name="echo", arguments={"message": "payload"}),
                ],
                finish_reason="tool_calls",
            ),
            ChatCompletionResponse(content="Finished.", finish_reason="stop"),
        ]
    )
    runtime = build_runtime(
        conversation_service,
        tool_registry,
        tool_executor,
        llm,
    )

    result = await runtime.execute(
        test_agent,
        AgentRunRequest(conversation_id="conv-2", input="Use tool"),
    )

    assert result.output == "Finished."
    assert result.iterations == 2
    assert result.tool_calls == ["tc-1"]
    assert len(llm.requests) == 2
    assert llm.requests[0].tools[0].name == "echo"


@pytest.mark.asyncio
async def test_agent_runtime_raises_on_max_iterations(
    conversation_service,
    tool_registry,
    tool_executor,
    test_agent,
) -> None:
    llm = MockLLMService(
        [
            ChatCompletionResponse(
                content=None,
                tool_calls=[
                    ToolCall(id=f"tc-{index}", name="echo", arguments={"message": "x"}),
                ],
                finish_reason="tool_calls",
            )
            for index in range(5)
        ]
    )
    runtime = build_runtime(
        conversation_service,
        tool_registry,
        tool_executor,
        llm,
    )

    with pytest.raises(AgentMaxIterationsError):
        await runtime.execute(
            test_agent,
            AgentRunRequest(conversation_id="conv-3", input="Loop"),
        )
