import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import get_lead_capture_service
from app.core.di.container import RuntimeContainer
from app.main import app
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.notifications.service import NotificationService
from tests.services.test_notification_service import MockEmailProvider
from tests.agents.lead_agent.conftest import MockLeadExtractionClient


@pytest.fixture
def api_runtime(settings) -> RuntimeContainer:
    return RuntimeContainer(settings)


@pytest.fixture
def api_client(api_runtime, db_session, company) -> TestClient:
    lead_repository = LeadRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [
                LeadCaptureLLMOutput(
                    reply="Thanks! What service do you need?",
                    name="Jane Doe",
                    phone="555-0100",
                ),
            ]
        ),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
    )

    app.dependency_overrides[get_lead_capture_service] = lambda: service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_lead_message_endpoint_returns_expected_shape(
    api_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = api_client.post(
        "/api/v1/agents/lead/message",
        json={
            "conversation_id": "api-conv-1",
            "message": "Hi, I'm Jane Doe at 555-0100 in Austin.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Thanks! What service do you need?"
    assert body["lead_complete"] is False
    assert "service_requested" in body["missing_fields"]
    assert body["extracted_data"]["name"] == "Jane Doe"
    assert body["lead_id"] is None


def test_lead_message_endpoint_validates_payload(
    api_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = api_client.post(
        "/api/v1/agents/lead/message",
        json={"conversation_id": "", "message": ""},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_lead_message_endpoint_requires_authentication(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/agents/lead/message",
        json={
            "conversation_id": "api-conv-unauth",
            "message": "Hello",
        },
    )

    assert response.status_code == 401
