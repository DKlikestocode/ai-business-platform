from typing import Any, Protocol, runtime_checkable

from app.core.agent_engine.context import AgentRunRequest, AgentRunResult
from app.core.tools.models import ToolCall, ToolResult
from app.core.workflows.models import WorkflowContext, WorkflowResult


@runtime_checkable
class WorkflowHandler(Protocol):
    """Contract for workflow step handlers."""

    async def handle_agent_step(
        self,
        agent_name: str,
        request: AgentRunRequest,
    ) -> AgentRunResult:
        """Execute an agent step."""

    async def handle_tool_step(
        self,
        tool_call: ToolCall,
        context: WorkflowContext,
    ) -> ToolResult:
        """Execute a tool step."""

    async def handle_llm_step(
        self,
        prompt: str,
        context: WorkflowContext,
    ) -> str:
        """Execute a direct LLM step."""

    async def handle_transform_step(
        self,
        expression: str,
        context: WorkflowContext,
    ) -> Any:
        """Transform workflow variables."""
