from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStepType(StrEnum):
    AGENT = "agent"
    TOOL = "tool"
    LLM = "llm"
    TRANSFORM = "transform"


class WorkflowStep(BaseModel):
    id: str
    type: WorkflowStepType
    name: str
    config: dict[str, Any] = Field(default_factory=dict)
    next_step_id: str | None = None


class WorkflowDefinition(BaseModel):
    id: str
    name: str
    description: str = ""
    steps: list[WorkflowStep] = Field(default_factory=list)
    entry_step_id: str


class WorkflowContext(BaseModel):
    workflow_id: str
    conversation_id: str
    variables: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowStepResult(BaseModel):
    step_id: str
    step_name: str
    output: Any = None
    success: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowResult(BaseModel):
    workflow_id: str
    conversation_id: str
    outputs: list[WorkflowStepResult] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
