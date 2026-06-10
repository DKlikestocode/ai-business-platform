import uuid

import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import get_lead_capture_service
from app.main import app
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.notifications.service import NotificationService
from tests.services.test_notification_service import MockEmailProvider
from tests.agents.lead_agent.conftest import MockLeadExtractionClient


@pytest.fixture
def widget_client(db_session, company) -> TestClient:
    lead_repository = LeadRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [
                LeadCaptureLLMOutput(
                    reply="Thanks! What service do you need?",
                    name="Widget User",
                    phone="555-0199",
                    location="Berlin",
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


@pytest.fixture
def complete_widget_client(db_session, company) -> TestClient:
    lead_repository = LeadRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [
                LeadCaptureLLMOutput(
                    reply="Thanks, we have everything we need.",
                    summary="Widget lead summary",
                    name="Widget User",
                    phone="555-0199",
                    location="Berlin",
                    service_requested="Roof repair",
                    description="Leak in kitchen",
                    urgency="high",
                    preferred_callback_time="Tomorrow morning",
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


def test_public_widget_message_success(widget_client: TestClient, company) -> None:
    response = widget_client.post(
        "/api/v1/public/widget/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "widget-conv-1",
            "message": "Hi, I'm looking for help in Berlin.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Thanks! What service do you need?"
    assert body["lead_complete"] is False
    assert body["extracted_data"]["name"] == "Widget User"
    assert body["extracted_data"]["location"] == "Berlin"


def test_public_widget_rate_limit_returns_429(widget_client: TestClient) -> None:
    payload = {
        "company_slug": "missing-company-slug",
        "conversation_id": "widget-rate-limit",
        "message": "Hello",
    }

    for _ in range(30):
        response = widget_client.post("/api/v1/public/widget/message", json=payload)
        assert response.status_code == 404

    response = widget_client.post("/api/v1/public/widget/message", json=payload)
    assert response.status_code == 429


def test_public_widget_unknown_company_slug_returns_404(widget_client: TestClient) -> None:
    response = widget_client.post(
        "/api/v1/public/widget/message",
        json={
            "company_slug": "missing-company-slug",
            "conversation_id": "widget-conv-404",
            "message": "Hello",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Company 'missing-company-slug' not found."


def test_public_widget_empty_message_returns_422(widget_client: TestClient, company) -> None:
    response = widget_client.post(
        "/api/v1/public/widget/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "widget-conv-empty",
            "message": "   ",
        },
    )

    assert response.status_code == 422


def test_public_widget_lead_persists_under_resolved_company(
    complete_widget_client: TestClient,
    company,
    lead_repository: LeadRepository,
) -> None:
    response = complete_widget_client.post(
        "/api/v1/public/widget/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "widget-conv-complete",
            "message": "I need urgent roof repair tomorrow morning.",
        },
    )

    assert response.status_code == 200
    assert response.json()["lead_complete"] is True
    assert response.json()["lead_id"] is not None

    lead = lead_repository.get_by_conversation("widget-conv-complete", company_id=company.id)
    assert lead is not None
    assert lead.name == "Widget User"
    assert lead.service_requested == "Roof repair"
    assert lead.status == "new"


def test_public_widget_does_not_leak_across_tenants(
    complete_widget_client: TestClient,
    company,
    company_repository,
    lead_repository: LeadRepository,
) -> None:
    suffix = uuid.uuid4().hex[:8]
    other_company = company_repository.create(
        name=f"Widget Other Co {suffix}",
        email=f"widget-other-{suffix}@example.com",
    )

    response = complete_widget_client.post(
        "/api/v1/public/widget/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "widget-tenant-isolation",
            "message": "I need urgent roof repair tomorrow morning.",
        },
    )

    assert response.status_code == 200

    tenant_lead = lead_repository.get_by_conversation(
        "widget-tenant-isolation",
        company_id=company.id,
    )
    other_lead = lead_repository.get_by_conversation(
        "widget-tenant-isolation",
        company_id=other_company.id,
    )

    assert tenant_lead is not None
    assert other_lead is None
