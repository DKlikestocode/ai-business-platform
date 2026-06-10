import logging
from typing import Any

from app.core.agent_engine.context import AgentRunRequest, AgentRunResult
from app.core.agent_engine.interface import Agent
from app.core.agent_engine.runtime import AgentRuntime
from app.core.conversation.service import ConversationService
from app.core.llm.interface import LLMService
from app.core.llm.models import ChatCompletionRequest, ChatMessage
from app.core.tools.models import ToolCall, ToolResult
from app.core.tools.registry import ToolExecutor, ToolRegistry
from app.core.workflows.interface import WorkflowHandler
from app.core.workflows.models import WorkflowContext

logger = logging.getLogger(__name__)


class RuntimeWorkflowHandler(WorkflowHandler):
    """Bridges workflow execution to the agent runtime."""

    def __init__(
        self,
        *,
        agent_runtime: AgentRuntime,
        agent_registry: dict[str, Agent],
        llm_service: LLMService,
        tool_executor: ToolExecutor,
    ) -> None:
        self._agent_runtime = agent_runtime
        self._agent_registry = agent_registry
        self._llm_service = llm_service
        self._tool_executor = tool_executor

    async def handle_agent_step(
        self,
        agent_name: str,
        request: AgentRunRequest,
    ) -> AgentRunResult:
        agent = self._agent_registry.get(agent_name)
        if agent is None:
            raise KeyError(f"Agent '{agent_name}' is not registered.")
        return await self._agent_runtime.execute(agent, request)

    async def handle_tool_step(
        self,
        tool_call: ToolCall,
        context: WorkflowContext,
    ) -> ToolResult:
        from app.core.agent_engine.context import AgentContext

        agent_context = AgentContext(
            conversation_id=context.conversation_id,
            agent_name="workflow",
            metadata=context.metadata,
        )
        return await self._tool_executor.execute(tool_call, agent_context)

    async def handle_llm_step(self, prompt: str, context: WorkflowContext) -> str:
        response = await self._llm_service.chat_completion(
            ChatCompletionRequest(
                messages=[ChatMessage(role="user", content=prompt)],
                metadata={"workflow_id": context.workflow_id},
            )
        )
        return response.content or ""

    async def handle_transform_step(
        self,
        expression: str,
        context: WorkflowContext,
    ) -> Any:
        if expression == "pass_through":
            return context.variables.get("input")
        if expression.startswith("get:"):
            key = expression.removeprefix("get:")
            return context.variables.get(key)
        return expression
