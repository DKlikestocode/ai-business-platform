from typing import Any

from app.core.agent_engine.context import AgentContext
from app.core.exceptions import ToolExecutionError, ToolNotFoundError
from app.core.tools.interface import Tool
from app.core.tools.models import ToolCall, ToolDefinition, ToolResult


class ToolRegistry:
    """Registry for tool lookup and LLM schema generation."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.definition.name] = tool

    def register_many(self, tools: list[Tool]) -> None:
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> Tool:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFoundError(f"Tool '{name}' is not registered.")
        return tool

    def resolve(self, names: list[str]) -> list[Tool]:
        return [self.get(name) for name in names]

    def list_definitions(self, names: list[str] | None = None) -> list[ToolDefinition]:
        if names is None:
            return [tool.definition for tool in self._tools.values()]
        return [self.get(name).definition for name in names]

    def __contains__(self, name: str) -> bool:
        return name in self._tools


class ToolExecutor:
    """Executes tool calls produced by the LLM."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    async def execute(
        self,
        tool_call: ToolCall,
        context: AgentContext,
    ) -> ToolResult:
        tool = self._registry.get(tool_call.name)
        try:
            result = await tool.execute(tool_call.arguments, context)
            return result.model_copy(
                update={
                    "tool_call_id": tool_call.id,
                    "name": tool_call.name,
                }
            )
        except ToolNotFoundError:
            raise
        except Exception as exc:
            raise ToolExecutionError(
                f"Tool '{tool_call.name}' failed: {exc}",
            ) from exc

    async def execute_many(
        self,
        tool_calls: list[ToolCall],
        context: AgentContext,
    ) -> list[ToolResult]:
        results: list[ToolResult] = []
        for tool_call in tool_calls:
            results.append(await self.execute(tool_call, context))
        return results
