import pytest

from app.core.agent_engine.context import AgentRunRequest
from app.core.agent_engine.workflow_handler import RuntimeWorkflowHandler
from app.core.llm.models import ChatCompletionResponse
from app.core.workflows.executor import WorkflowExecutor
from app.core.workflows.models import (
    WorkflowContext,
    WorkflowDefinition,
    WorkflowStep,
    WorkflowStepType,
)
from tests.conftest import MockLLMService, build_runtime


@pytest.mark.asyncio
async def test_workflow_executor_runs_agent_and_transform_steps(
    conversation_service,
    tool_registry,
    tool_executor,
    test_agent,
) -> None:
    llm = MockLLMService(
        [ChatCompletionResponse(content="Workflow output", finish_reason="stop")]
    )
    runtime = build_runtime(
        conversation_service,
        tool_registry,
        tool_executor,
        llm,
    )
    handler = RuntimeWorkflowHandler(
        agent_runtime=runtime,
        agent_registry={test_agent.name: test_agent},
        llm_service=llm,
        tool_executor=tool_executor,
    )
    executor = WorkflowExecutor(handler)

    workflow = WorkflowDefinition(
        id="wf-1",
        name="Test Workflow",
        entry_step_id="step-1",
        steps=[
            WorkflowStep(
                id="step-1",
                type=WorkflowStepType.AGENT,
                name="agent_step",
                config={"agent_name": "test-agent", "input": "Start"},
                next_step_id="step-2",
            ),
            WorkflowStep(
                id="step-2",
                type=WorkflowStepType.TRANSFORM,
                name="transform_step",
                config={"expression": "get:agent_step"},
            ),
        ],
    )

    result = await executor.execute(
        workflow,
        WorkflowContext(workflow_id="wf-1", conversation_id="conv-wf-1"),
    )

    assert result.success is True
    assert result.variables["agent_step"] == "Workflow output"
    assert result.variables["transform_step"] == "Workflow output"
    assert len(result.outputs) == 2
