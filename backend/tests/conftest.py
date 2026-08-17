from typing import Any

import pytest

from app.config import Settings
from app.core.rate_limit import get_rate_limiter
from app.core.agent_engine.base import BaseAgent
from app.core.agent_engine.context import AgentContext, AgentRunRequest
from app.core.agent_engine.runtime import AgentRuntime
from app.core.conversation.service import ConversationService
from app.core.di.container import RuntimeContainer
from app.core.llm.models import ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from app.core.memory.in_memory import InMemoryStore
from app.core.prompts.builder import PromptBuilder
from app.core.tools.models import ToolCall, ToolDefinition, ToolParameterSchema, ToolResult
from app.core.tools.registry import ToolExecutor, ToolRegistry


class MockLLMService:
    def __init__(self, responses: list[ChatCompletionResponse]) -> None:
        self._responses = list(responses)
        self.requests: list[ChatCompletionRequest] = []

    async def chat_completion(
        self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        self.requests.append(request)
        if not self._responses:
            raise RuntimeError("No mock responses left.")
        return self._responses.pop(0)


class EchoTool:
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="echo",
            description="Echo input back",
            parameters=ToolParameterSchema(
                properties={"message": {"type": "string"}},
                required=["message"],
            ),
        )

    async def execute(
        self,
        arguments: dict[str, Any],
        context: AgentContext,
    ) -> ToolResult:
        message = str(arguments.get("message", ""))
        return ToolResult(
            tool_call_id="tool-call-1",
            name="echo",
            output=message,
        )


@pytest.fixture(autouse=True)
def reset_rate_limiter() -> None:
    get_rate_limiter().reset()


@pytest.fixture
def settings() -> Settings:
    return Settings(
        openai_api_key="test-key",
        openai_model="gpt-test",
        agent_max_iterations=4,
    )


@pytest.fixture
def memory_store() -> InMemoryStore:
    return InMemoryStore()


@pytest.fixture
def prompt_builder() -> PromptBuilder:
    return PromptBuilder()


@pytest.fixture
def conversation_service(
    memory_store: InMemoryStore,
    prompt_builder: PromptBuilder,
) -> ConversationService:
    return ConversationService(memory_store, prompt_builder)


@pytest.fixture
def tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(EchoTool())
    return registry


@pytest.fixture
def tool_executor(tool_registry: ToolRegistry) -> ToolExecutor:
    return ToolExecutor(tool_registry)


@pytest.fixture
def test_agent() -> BaseAgent:
    return BaseAgent(
        name="test-agent",
        description="Test agent",
        tool_names=["echo"],
        system_prompt="You are a test agent.",
    )


@pytest.fixture
def runtime_container(settings: Settings) -> RuntimeContainer:
    return RuntimeContainer(settings)


def build_runtime(
    conversation_service: ConversationService,
    tool_registry: ToolRegistry,
    tool_executor: ToolExecutor,
    llm_service: MockLLMService,
) -> AgentRuntime:
    return AgentRuntime(
        llm_service=llm_service,
        conversation_service=conversation_service,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
        max_iterations=4,
    )


@pytest.fixture
def db_session():
    from app.db.session import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def company_repository(db_session):
    from app.repositories.company_repository import CompanyRepository

    return CompanyRepository(db_session)


@pytest.fixture
def company(company_repository):
    import uuid

    suffix = uuid.uuid4().hex[:8]
    return company_repository.create(
        name=f"Test Company {suffix}",
        email=f"test-{suffix}@example.com",
    )


@pytest.fixture
def user_repository(db_session):
    from app.repositories.user_repository import UserRepository

    return UserRepository(db_session)


@pytest.fixture
def conversation_repository(db_session):
    from app.repositories.conversation_repository import ConversationRepository

    return ConversationRepository(db_session)


@pytest.fixture
def agent_repository(db_session):
    from app.repositories.agent_repository import AgentRepository

    return AgentRepository(db_session)


@pytest.fixture
def lead_repository(db_session):
    from app.agents.lead_agent.repository import LeadRepository

    return LeadRepository(db_session)


@pytest.fixture
def intake_repository(db_session):
    from app.repositories.intake_repository import IntakeRepository

    return IntakeRepository(db_session)


@pytest.fixture
def company_activation_repository(db_session):
    from app.repositories.company_activation_repository import CompanyActivationRepository

    return CompanyActivationRepository(db_session)


@pytest.fixture
def dev_client(db_session) -> "TestClient":
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


@pytest.fixture
def auth_user(user_repository, company):
    import uuid

    from app.core.security import hash_password
    from app.db.models.enums import UserRole

    suffix = uuid.uuid4().hex[:8]
    return user_repository.create(
        company_id=company.id,
        first_name="Auth",
        last_name="User",
        email=f"auth-user-{suffix}@example.com",
        password_hash=hash_password("secure-password"),
        role=UserRole.MEMBER,
    )


@pytest.fixture
def auth_headers(dev_client, auth_user) -> dict[str, str]:
    response = dev_client.post(
        "/api/v1/auth/login",
        json={"email": auth_user.email, "password": "secure-password"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
