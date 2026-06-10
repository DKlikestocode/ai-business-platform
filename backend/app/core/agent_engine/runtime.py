import logging

from app.core.agent_engine.context import AgentContext, AgentRunRequest, AgentRunResult
from app.core.agent_engine.interface import Agent
from app.core.conversation.service import ConversationService
from app.core.exceptions import AgentMaxIterationsError
from app.core.llm.interface import LLMService
from app.core.llm.models import ChatCompletionRequest
from app.core.tools.registry import ToolExecutor, ToolRegistry

logger = logging.getLogger(__name__)


class AgentRuntime:
    """Executes any agent using shared runtime services."""

    def __init__(
        self,
        *,
        llm_service: LLMService,
        conversation_service: ConversationService,
        tool_registry: ToolRegistry,
        tool_executor: ToolExecutor,
        max_iterations: int = 8,
    ) -> None:
        self._llm_service = llm_service
        self._conversation_service = conversation_service
        self._tool_registry = tool_registry
        self._tool_executor = tool_executor
        self._max_iterations = max_iterations

    async def execute(self, agent: Agent, request: AgentRunRequest) -> AgentRunResult:
        context = AgentContext(
            conversation_id=request.conversation_id,
            agent_name=agent.name,
            user_id=request.user_id,
            metadata=request.metadata,
        )

        await agent.on_run_start(request)
        await self._conversation_service.record_user_message(
            request.conversation_id,
            request.input,
        )

        system_prompt = await agent.build_system_prompt(context)
        tool_definitions = self._tool_registry.list_definitions(agent.get_tool_names())
        tool_call_ids: list[str] = []

        for iteration in range(1, self._max_iterations + 1):
            messages = await self._conversation_service.build_messages(
                request.conversation_id,
                system_prompt,
            )
            response = await self._llm_service.chat_completion(
                ChatCompletionRequest(
                    messages=messages,
                    tools=tool_definitions,
                    metadata={"agent": agent.name, "iteration": iteration},
                )
            )

            if response.requires_tool_execution:
                await self._conversation_service.record_assistant_tool_calls(
                    request.conversation_id,
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
                for tool_call in response.tool_calls:
                    tool_call_ids.append(tool_call.id)
                    result = await self._tool_executor.execute(tool_call, context)
                    await self._conversation_service.record_tool_result(
                        request.conversation_id,
                        tool_call_id=result.tool_call_id,
                        tool_name=result.name,
                        output=result.output,
                    )
                continue

            output = response.content or ""
            await self._conversation_service.record_assistant_message(
                request.conversation_id,
                output,
            )
            history = await self._conversation_service.get_history(request.conversation_id)
            result = AgentRunResult(
                conversation_id=request.conversation_id,
                agent_name=agent.name,
                output=output,
                messages=history,
                tool_calls=tool_call_ids,
                iterations=iteration,
                metadata={"finish_reason": response.finish_reason},
            )
            await agent.on_run_complete(result)
            logger.info(
                "Agent '%s' completed in %s iteration(s) for conversation '%s'",
                agent.name,
                iteration,
                request.conversation_id,
            )
            return result

        raise AgentMaxIterationsError(
            f"Agent '{agent.name}' exceeded max iterations ({self._max_iterations}).",
        )
