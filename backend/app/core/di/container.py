from functools import lru_cache
from typing import TYPE_CHECKING

from app.config import Settings, get_settings
from app.core.agent_engine.runtime import AgentRuntime
from app.core.agent_engine.workflow_handler import RuntimeWorkflowHandler
from app.core.conversation.service import ConversationService
from app.core.llm.openai_service import OpenAIService
from app.core.memory.in_memory import InMemoryStore
from app.core.prompts.builder import PromptBuilder
from app.core.tools.registry import ToolExecutor, ToolRegistry
from app.core.workflows.executor import WorkflowExecutor

if TYPE_CHECKING:
    from app.core.agent_engine.interface import Agent
    from app.core.tools.interface import Tool


class RuntimeContainer:
    """Dependency injection container for the agent runtime core."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._memory_store = InMemoryStore()
        self._prompt_builder = PromptBuilder()
        self._tool_registry = ToolRegistry()
        self._agents: dict[str, Agent] = {}

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def memory_store(self) -> InMemoryStore:
        return self._memory_store

    @property
    def prompt_builder(self) -> PromptBuilder:
        return self._prompt_builder

    @property
    def tool_registry(self) -> ToolRegistry:
        return self._tool_registry

    @property
    def tool_executor(self) -> ToolExecutor:
        return ToolExecutor(self._tool_registry)

    @property
    def conversation_service(self) -> ConversationService:
        return ConversationService(self._memory_store, self._prompt_builder)

    @property
    def llm_service(self) -> OpenAIService:
        return OpenAIService(
            api_key=self._settings.openai_api_key,
            model=self._settings.openai_model,
            base_url=self._settings.openai_base_url,
            organization=self._settings.openai_organization,
            timeout=self._settings.openai_timeout,
        )

    @property
    def agent_runtime(self) -> AgentRuntime:
        return AgentRuntime(
            llm_service=self.llm_service,
            conversation_service=self.conversation_service,
            tool_registry=self._tool_registry,
            tool_executor=self.tool_executor,
            max_iterations=self._settings.agent_max_iterations,
        )

    @property
    def workflow_handler(self) -> RuntimeWorkflowHandler:
        return RuntimeWorkflowHandler(
            agent_runtime=self.agent_runtime,
            agent_registry=self._agents,
            llm_service=self.llm_service,
            tool_executor=self.tool_executor,
        )

    @property
    def workflow_executor(self) -> WorkflowExecutor:
        return WorkflowExecutor(self.workflow_handler)

    def register_tool(self, tool: Tool) -> None:
        self._tool_registry.register(tool)

    def register_agent(self, agent: Agent) -> None:
        self._agents[agent.name] = agent


@lru_cache
def get_runtime_container() -> RuntimeContainer:
    return RuntimeContainer()
