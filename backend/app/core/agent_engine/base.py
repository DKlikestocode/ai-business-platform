from app.core.agent_engine.context import AgentContext, AgentRunRequest, AgentRunResult


class BaseAgent:
    """Base agent with default lifecycle hooks for extension."""

    def __init__(
        self,
        *,
        name: str,
        description: str,
        tool_names: list[str] | None = None,
        system_prompt: str = "You are a helpful AI assistant.",
    ) -> None:
        self._name = name
        self._description = description
        self._tool_names = tool_names or []
        self._system_prompt = system_prompt

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def get_tool_names(self) -> list[str]:
        return list(self._tool_names)

    async def build_system_prompt(self, context: AgentContext) -> str:
        return self._system_prompt

    async def on_run_start(self, request: AgentRunRequest) -> None:
        return None

    async def on_run_complete(self, result: AgentRunResult) -> None:
        return None
