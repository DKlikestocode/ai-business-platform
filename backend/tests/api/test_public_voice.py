import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import get_voice_lead_capture_service
from app.config import Settings, get_settings
from app.db.models.enums import ConversationChannel
from app.main import app
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.notifications.service import NotificationService
from tests.services.test_notification_service import MockEmailProvider
from tests.agents.lead_agent.conftest import MockLeadExtractionClient


@pytest.fixture
def voice_client(db_session, company) -> TestClient:
    lead_repository = LeadRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [
                LeadCaptureLLMOutput(
                    reply="Danke! Was genau ist das Problem?",
                    name="Phone Caller",
                    location="Berlin",
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


@pytest.fixture
def complete_voice_client(db_session, company) -> TestClient:
    lead_repository = LeadRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [
                LeadCaptureLLMOutput(
                    reply="Vielen Dank, wir melden uns.",
                    summary="Phone lead summary",
                    name="Phone Caller",
                    phone="01701234599",
                    location="Berlin",
                    postal_code="10115",
                    service_requested="Rohrbruch",
                    description="Wasser im Keller",
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


def test_public_voice_message_success(voice_client: TestClient, company) -> None:
    response = voice_client.post(
        "/api/v1/public/voice/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "voice-conv-1",
            "message": "Hallo, ich habe einen Rohrbruch in Berlin.",
            "caller_phone": "+491701234567",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Danke! Was genau ist das Problem?"


def test_public_voice_unknown_company_slug_returns_404(voice_client: TestClient) -> None:
    response = voice_client.post(
        "/api/v1/public/voice/message",
        json={
            "company_slug": "missing-company-slug",
            "conversation_id": "voice-conv-404",
            "message": "Hallo",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Company 'missing-company-slug' not found."


def test_public_voice_empty_message_returns_422(voice_client: TestClient, company) -> None:
    response = voice_client.post(
        "/api/v1/public/voice/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "voice-conv-empty",
            "message": "   ",
        },
    )

    assert response.status_code == 422


def test_public_voice_lead_persists_under_resolved_company(
    complete_voice_client: TestClient,
    company,
    lead_repository: LeadRepository,
) -> None:
    response = complete_voice_client.post(
        "/api/v1/public/voice/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "voice-conv-complete",
            "message": "Dringender Rohrbruch, Rückruf heute Nachmittag.",
            "caller_phone": "+491701234567",
        },
    )

    assert response.status_code == 200

    lead = lead_repository.get_by_conversation("voice-conv-complete", company_id=company.id)
    assert lead is not None
    assert lead.service_requested == "Rohrbruch"


def test_public_voice_does_not_leak_across_tenants(
    complete_voice_client: TestClient,
    company,
    company_repository,
    lead_repository: LeadRepository,
) -> None:
    suffix = uuid.uuid4().hex[:8]
    other_company = company_repository.create(
        name=f"Voice Other Co {suffix}",
        email=f"voice-other-{suffix}@example.com",
    )

    response = complete_voice_client.post(
        "/api/v1/public/voice/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "voice-tenant-isolation",
            "message": "Dringender Rohrbruch in Berlin.",
            "caller_phone": "+491701234567",
        },
    )

    assert response.status_code == 200

    tenant_lead = lead_repository.get_by_conversation(
        "voice-tenant-isolation",
        company_id=company.id,
    )
    other_lead = lead_repository.get_by_conversation(
        "voice-tenant-isolation",
        company_id=other_company.id,
    )

    assert tenant_lead is not None
    assert other_lead is None


def test_public_voice_webhook_tool_calls(voice_client: TestClient, company) -> None:
    response = voice_client.post(
        "/api/v1/public/voice/webhook",
        json={
            "message": {
                "type": "tool-calls",
                "call": {
                    "id": "vapi-call-1",
                    "metadata": {"company_slug": company.slug},
                    "customer": {"number": "+491701234567"},
                },
                "toolCallList": [
                    {
                        "id": "tool-call-1",
                        "type": "function",
                        "function": {
                            "name": "capture_inquiry",
                            "arguments": json.dumps(
                                {"message": "Ich brauche Hilfe wegen eines Rohrbruchs."},
                            ),
                        },
                    }
                ],
            }
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["result"] == "Danke! Was genau ist das Problem?"


def _voice_webhook_payload(company_slug: str) -> dict:
    return {
        "message": {
            "type": "tool-calls",
            "call": {
                "id": "vapi-call-secret",
                "metadata": {"company_slug": company_slug},
                "customer": {"number": "+491701234567"},
            },
            "toolCallList": [
                {
                    "id": "tool-call-secret",
                    "type": "function",
                    "function": {
                        "name": "capture_inquiry",
                        "arguments": json.dumps({"message": "Rohrbruch in Berlin"}),
                    },
                }
            ],
        }
    }


def test_public_voice_webhook_rejects_missing_secret_when_configured(
    voice_client: TestClient,
    company,
) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        vapi_webhook_secret="pilot-secret",
    )
    try:
        response = voice_client.post(
            "/api/v1/public/voice/webhook",
            json=_voice_webhook_payload(company.slug),
        )
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 401


def test_public_voice_webhook_accepts_matching_secret(
    voice_client: TestClient,
    company,
) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        vapi_webhook_secret="pilot-secret",
    )
    try:
        response = voice_client.post(
            "/api/v1/public/voice/webhook",
            json=_voice_webhook_payload(company.slug),
            headers={"X-Vapi-Secret": "pilot-secret"},
        )
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 200


def test_public_voice_end_of_call_returns_204(voice_client: TestClient) -> None:
    response = voice_client.post("/api/v1/public/voice/end-of-call", json={})
    assert response.status_code == 204
