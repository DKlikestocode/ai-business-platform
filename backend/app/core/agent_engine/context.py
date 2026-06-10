from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.core.memory.models import ConversationMessage, MessageRole


class AgentContext(BaseModel):
    conversation_id: str
    agent_name: str
    user_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentRunRequest(BaseModel):
    conversation_id: str
    input: str
    user_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRunResult(BaseModel):
    conversation_id: str
    agent_name: str
    output: str
    messages: list[ConversationMessage] = Field(default_factory=list)
    tool_calls: list[str] = Field(default_factory=list)
    iterations: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRunState(BaseModel):
    request: AgentRunRequest
    context: AgentContext
    system_prompt: str = ""
    iterations: int = 0
    tool_call_ids: list[str] = Field(default_factory=list)
    finished: bool = False
    output: str = ""
