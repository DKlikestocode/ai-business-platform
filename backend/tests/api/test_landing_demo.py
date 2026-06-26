import uuid

import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import get_landing_demo_lead_capture_service
from app.api.schemas.landing_demo import LANDING_DEMO_CONVERSATION_PREFIX
from app.config import get_settings
from app.db.models.enums import ConversationChannel
from app.demo.seed import DEMO_COMPANY_SLUG
from app.main import app
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.notifications.service import NotificationService
from tests.agents.lead_agent.conftest import MockLeadExtractionClient
from tests.services.test_notification_service import MockEmailProvider

_COMPLETE_OUTPUT = LeadCaptureLLMOutput(
    reply="Danke, wir haben alle nötigen Angaben.",
    summary="Landing demo summary",
    name="Demo Besucher",
    phone="01701234599",
    location="Berlin",
    postal_code="10115",
    service_requested="Sanitär",
    description="Undichte Spüle",
    urgency="hoch",
    preferred_callback_time="Heute",
)


@pytest.fixture
def landing_demo_client(db_session) -> TestClient:
    lead_repository = LeadRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [LeadCaptureLLMOutput(reply="Danke! Wie kann ich helfen?")]
        ),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        activation_repository=CompanyActivationRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
        channel=ConversationChannel.LANDING_DEMO,
    )
    app.dependency_overrides[get_landing_demo_lead_capture_service] = lambda: service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def landing_demo_complete_client(db_session) -> TestClient:
    lead_repository = LeadRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient([_COMPLETE_OUTPUT]),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        activation_repository=CompanyActivationRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
        channel=ConversationChannel.LANDING_DEMO,
    )
    app.dependency_overrides[get_landing_demo_lead_capture_service] = lambda: service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_landing_demo_message_returns_live_reply(
    landing_demo_client: TestClient,
) -> None:
    response = landing_demo_client.post(
        "/api/v1/public/landing-demo/message",
        json={
            "conversation_id": f"{LANDING_DEMO_CONVERSATION_PREFIX}test-1",
            "message": "Wir haben einen Sanitär-Notfall.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Danke! Wie kann ich helfen?"
    assert body["lead_complete"] is False


def test_landing_demo_rejects_invalid_conversation_id(
    landing_demo_client: TestClient,
) -> None:
    response = landing_demo_client.post(
        "/api/v1/public/landing-demo/message",
        json={
            "conversation_id": "widget-conv-1",
            "message": "Hallo",
        },
    )

    assert response.status_code == 422


def test_landing_demo_does_not_persist_lead(
    landing_demo_complete_client: TestClient,
    db_session,
) -> None:
    conversation_id = f"{LANDING_DEMO_CONVERSATION_PREFIX}no-persist"
    response = landing_demo_complete_client.post(
        "/api/v1/public/landing-demo/message",
        json={
            "conversation_id": conversation_id,
            "message": "Unsere Spüle läuft aus.",
        },
    )
    assert response.status_code == 200
    assert response.json()["lead_complete"] is True
    assert response.json()["lead_id"] is None

    company_repository = CompanyRepository(db_session)
    company = company_repository.get_by_slug(DEMO_COMPANY_SLUG)
    assert company is not None

    lead_repository = LeadRepository(db_session)
    assert lead_repository.get_by_conversation(conversation_id, company_id=company.id) is None


def test_landing_demo_message_limit_returns_429(db_session) -> None:
    lead_repository = LeadRepository(db_session)
    settings = get_settings()
    outputs = [
        LeadCaptureLLMOutput(reply=f"Antwort {index}")
        for index in range(settings.landing_demo_max_user_messages + 1)
    ]
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(outputs),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        activation_repository=CompanyActivationRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
        channel=ConversationChannel.LANDING_DEMO,
    )
    app.dependency_overrides[get_landing_demo_lead_capture_service] = lambda: service
    client = TestClient(app)
    conversation_id = f"{LANDING_DEMO_CONVERSATION_PREFIX}limit-{uuid.uuid4()}"

    try:
        for index in range(settings.landing_demo_max_user_messages):
            response = client.post(
                "/api/v1/public/landing-demo/message",
                json={
                    "conversation_id": conversation_id,
                    "message": f"Nachricht {index}",
                },
            )
            assert response.status_code == 200

        limit_response = client.post(
            "/api/v1/public/landing-demo/message",
            json={
                "conversation_id": conversation_id,
                "message": "Eine Nachricht zu viel",
            },
        )
        assert limit_response.status_code == 429
    finally:
        app.dependency_overrides.clear()
