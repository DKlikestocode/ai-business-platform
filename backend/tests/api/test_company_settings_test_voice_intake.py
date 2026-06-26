import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import get_voice_lead_capture_service
from app.db.models.enums import ConversationChannel
from app.main import app
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.notifications.service import NotificationService
from tests.agents.lead_agent.conftest import MockLeadExtractionClient
from tests.services.test_notification_service import MockEmailProvider


@pytest.fixture
def voice_intake_client(db_session) -> TestClient:
    lead_repository = LeadRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [
                LeadCaptureLLMOutput(
                    reply="Vielen Dank, wir melden uns.",
                    summary="Simulated phone inquiry",
                    name="Max Test",
                    phone="01701234567",
                    location="München",
                    postal_code="80331",
                    service_requested="Rohrbruch",
                    description="Wasserrohrbruch in der Küche",
                    urgency="high",
                    preferred_callback_time="Heute Nachmittag",
                ),
            ]
        ),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        activation_repository=CompanyActivationRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
        channel=ConversationChannel.VOICE,
    )
    app.dependency_overrides[get_voice_lead_capture_service] = lambda: service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_test_voice_intake_requires_authentication(
    voice_intake_client: TestClient,
) -> None:
    response = voice_intake_client.post("/api/v1/company/settings/test-voice-intake")
    assert response.status_code == 401


def test_test_voice_intake_creates_phone_lead(
    voice_intake_client: TestClient,
    auth_headers: dict[str, str],
    company,
    lead_repository: LeadRepository,
) -> None:
    response = voice_intake_client.post(
        "/api/v1/company/settings/test-voice-intake",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Vielen Dank, wir melden uns."
    assert body["lead_id"] is not None

    lead = lead_repository.get_by_id(body["lead_id"])
    assert lead is not None
    assert lead.service_requested == "Rohrbruch"


def test_test_voice_intake_scoped_to_authenticated_tenant(
    voice_intake_client: TestClient,
    auth_headers: dict[str, str],
    company,
    company_repository,
    lead_repository: LeadRepository,
) -> None:
    response = voice_intake_client.post(
        "/api/v1/company/settings/test-voice-intake",
        headers=auth_headers,
    )
    assert response.status_code == 200
    lead_id = response.json()["lead_id"]

    lead = lead_repository.get_by_id(lead_id)
    assert lead is not None
    assert lead.company_id == company.id
