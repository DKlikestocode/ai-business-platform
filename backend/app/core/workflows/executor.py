import logging

from app.core.agent_engine.context import AgentRunRequest
from app.core.exceptions import WorkflowExecutionError
from app.core.tools.models import ToolCall
from app.core.workflows.interface import WorkflowHandler
from app.core.workflows.models import (
    WorkflowContext,
    WorkflowDefinition,
    WorkflowResult,
    WorkflowStep,
    WorkflowStepResult,
    WorkflowStepType,
)

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Executes declarative workflows step-by-step."""

    def __init__(self, handler: WorkflowHandler) -> None:
        self._handler = handler

    async def execute(
        self,
        workflow: WorkflowDefinition,
        context: WorkflowContext,
    ) -> WorkflowResult:
        step_map = {step.id: step for step in workflow.steps}
        current_step = step_map.get(workflow.entry_step_id)
        if current_step is None:
            raise WorkflowExecutionError(
                f"Entry step '{workflow.entry_step_id}' not found in workflow '{workflow.id}'.",
            )

        outputs: list[WorkflowStepResult] = []
        visited: set[str] = set()

        while current_step is not None:
            if current_step.id in visited:
                raise WorkflowExecutionError(
                    f"Cycle detected at step '{current_step.id}' in workflow '{workflow.id}'.",
                )
            visited.add(current_step.id)

            step_result = await self._execute_step(current_step, context)
            outputs.append(step_result)
            if not step_result.success:
                return WorkflowResult(
                    workflow_id=workflow.id,
                    conversation_id=context.conversation_id,
                    outputs=outputs,
                    variables=context.variables,
                    success=False,
                )

            context.variables[current_step.name] = step_result.output

            next_step_id = current_step.next_step_id
            if next_step_id is None:
                break
            current_step = step_map.get(next_step_id)
            if current_step is None:
                raise WorkflowExecutionError(
                    f"Next step '{next_step_id}' not found in workflow '{workflow.id}'.",
                )

        return WorkflowResult(
            workflow_id=workflow.id,
            conversation_id=context.conversation_id,
            outputs=outputs,
            variables=context.variables,
            success=True,
        )

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext,
    ) -> WorkflowStepResult:
        logger.info("Executing workflow step '%s' (%s)", step.name, step.type)
        try:
            output = await self._dispatch(step, context)
            return WorkflowStepResult(
                step_id=step.id,
                step_name=step.name,
                output=output,
                success=True,
            )
        except Exception as exc:
            logger.exception("Workflow step '%s' failed", step.name)
            return WorkflowStepResult(
                step_id=step.id,
                step_name=step.name,
                output=str(exc),
                success=False,
                metadata={"error": str(exc)},
            )

    async def _dispatch(self, step: WorkflowStep, context: WorkflowContext) -> object:
        if step.type == WorkflowStepType.AGENT:
            agent_name = step.config["agent_name"]
            request = AgentRunRequest(
                conversation_id=context.conversation_id,
                input=step.config.get("input", context.variables.get("input", "")),
                metadata=context.metadata,
            )
            result = await self._handler.handle_agent_step(agent_name, request)
            return result.output

        if step.type == WorkflowStepType.TOOL:
            tool_call = ToolCall(
                id=step.config.get("tool_call_id", step.id),
                name=step.config["tool_name"],
                arguments=step.config.get("arguments", {}),
            )
            result = await self._handler.handle_tool_step(tool_call, context)
            return result.output

        if step.type == WorkflowStepType.LLM:
            prompt = step.config.get("prompt", "")
            return await self._handler.handle_llm_step(prompt, context)

        if step.type == WorkflowStepType.TRANSFORM:
            expression = step.config.get("expression", "")
            return await self._handler.handle_transform_step(expression, context)

        raise WorkflowExecutionError(f"Unsupported workflow step type: {step.type}")
