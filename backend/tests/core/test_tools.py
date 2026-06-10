import pytest

from app.core.exceptions import ToolNotFoundError
from tests.conftest import EchoTool


def test_tool_registry_register_and_resolve() -> None:
    from app.core.tools.registry import ToolRegistry

    registry = ToolRegistry()
    tool = EchoTool()
    registry.register(tool)

    assert "echo" in registry
    assert registry.get("echo") is tool
    assert registry.list_definitions(["echo"])[0].name == "echo"


def test_tool_registry_missing_tool_raises() -> None:
    from app.core.tools.registry import ToolRegistry

    registry = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        registry.get("missing")


@pytest.mark.asyncio
async def test_tool_executor_runs_registered_tool(
    tool_registry,
    tool_executor,
) -> None:
    from app.core.agent_engine.context import AgentContext
    from app.core.tools.models import ToolCall

    context = AgentContext(conversation_id="conv-1", agent_name="test")
    result = await tool_executor.execute(
        ToolCall(id="1", name="echo", arguments={"message": "hello"}),
        context,
    )

    assert result.success is True
    assert result.output == "hello"
