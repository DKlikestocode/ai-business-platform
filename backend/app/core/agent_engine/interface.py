from typing import Protocol, runtime_checkable

from app.core.agent_engine.context import AgentContext, AgentRunRequest, AgentRunResult


@runtime_checkable
class Agent(Protocol):
    """Contract for executable agents."""

    @property
    def name(self) -> str:
        """Unique agent identifier."""

    @property
    def description(self) -> str:
        """Human-readable agent purpose."""

    def get_tool_names(self) -> list[str]:
        """Return tool names this agent is allowed to use."""

    async def build_system_prompt(self, context: AgentContext) -> str:
        """Build the system prompt for the current run."""

    async def on_run_start(self, request: AgentRunRequest) -> None:
        """Optional hook invoked before execution begins."""

    async def on_run_complete(self, result: AgentRunResult) -> None:
        """Optional hook invoked after execution completes."""
