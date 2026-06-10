"""Core runtime exceptions."""


class RuntimeCoreError(Exception):
    """Base exception for agent runtime errors."""


class AgentNotFoundError(RuntimeCoreError):
    """Raised when a requested agent cannot be resolved."""


class ToolNotFoundError(RuntimeCoreError):
    """Raised when a requested tool is not registered."""


class ToolExecutionError(RuntimeCoreError):
    """Raised when a tool fails during execution."""


class AgentMaxIterationsError(RuntimeCoreError):
    """Raised when an agent exceeds its iteration limit."""


class LLMServiceError(RuntimeCoreError):
    """Raised when the LLM provider returns an error."""


class WorkflowExecutionError(RuntimeCoreError):
    """Raised when a workflow step fails."""


class MemoryError(RuntimeCoreError):
    """Raised when memory operations fail."""
