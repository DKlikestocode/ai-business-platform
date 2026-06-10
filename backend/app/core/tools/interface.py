from typing import Any, Protocol, runtime_checkable

from app.core.agent_engine.context import AgentContext
from app.core.tools.models import ToolDefinition, ToolResult


@runtime_checkable
class Tool(Protocol):
    """Contract for callable agent tools."""

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool schema exposed to the LLM."""

    async def execute(
        self,
        arguments: dict[str, Any],
        context: AgentContext,
    ) -> ToolResult:
        """Execute the tool with validated arguments."""
