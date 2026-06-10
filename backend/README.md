# Backend

FastAPI application for the AI Agent Platform.

## Agent Runtime Core

The runtime core lives under `app/core/` and provides reusable building blocks for any future agent.

| Module | Responsibility |
|--------|----------------|
| `agent_engine` | `Agent` protocol, `AgentRuntime`, lifecycle hooks |
| `tools` | `Tool` protocol, registry, executor |
| `memory` | `MemoryStore` protocol, in-memory implementation |
| `prompts` | `PromptBuilder` for LLM message assembly |
| `llm` | `LLMService` protocol, `OpenAIService` |
| `conversation` | Conversation history and prompt orchestration |
| `workflows` | Declarative workflow execution |
| `di` | `RuntimeContainer` dependency injection |

### Executing an agent

```python
from app.core.agent_engine import AgentRuntime, BaseAgent
from app.core.di import RuntimeContainer

container = RuntimeContainer()
container.register_agent(BaseAgent(name="demo", description="Demo agent"))
container.register_tool(my_tool)

runtime = container.agent_runtime
result = await runtime.execute(
    container._agents["demo"],
    AgentRunRequest(conversation_id="conv-1", input="Hello"),
)
```

## Development

The development container mounts `app/`, `alembic/`, and `tests/` for hot reload.

## Commands

```bash
# Run migrations
alembic upgrade head

# Seed demo leads (development)
python -m app.scripts.seed_demo_data

# Start API locally
uvicorn app.main:app --reload

# Run tests
pytest
```
