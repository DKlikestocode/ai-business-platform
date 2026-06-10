from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolParameterSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)
    additional_properties: bool = Field(
        default=False,
        serialization_alias="additionalProperties",
    )


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: ToolParameterSchema = Field(default_factory=ToolParameterSchema)


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool_call_id: str
    name: str
    output: str
    success: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
