import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import get_lead_capture_service, get_widget_lead_capture_service
from app.db.models.enums import ConversationChannel
from app.main import app
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.notifications.service import NotificationService
from tests.agents.lead_agent.conftest import MockLeadExtractionClient
from tests.services.test_notification_service import MockEmailProvider

_COMPLETE_WEBSITE_OUTPUT = LeadCaptureLLMOutput(
    reply="Thanks, we have everything we need.",
    summary="Website inquiry summary",
    name="Website User",
    phone="01701234599",
    location="Berlin",
    service_requested="Roof repair",
    description="Leak in kitchen",
    urgency="high",
    preferred_callback_time="Tomorrow morning",
)


def _build_widget_service(db_session) -> LeadCaptureService:
    lead_repository = LeadRepository(db_session)
    return LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient([_COMPLETE_WEBSITE_OUTPUT]),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        activation_repository=CompanyActivationRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
        channel=ConversationChannel.WEB,
    )


def _build_dashboard_service(db_session) -> LeadCaptureService:
    lead_repository = LeadRepository(db_session)
    return LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient([_COMPLETE_WEBSITE_OUTPUT]),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        activation_repository=CompanyActivationRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
        channel=ConversationChannel.DASHBOARD,
    )


@pytest.fixture
def widget_milestone_client(db_session) -> TestClient:
    app.dependency_overrides[get_widget_lead_capture_service] = (
        lambda: _build_widget_service(db_session)
    )
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def dashboard_milestone_client(db_session) -> TestClient:
    app.dependency_overrides[get_lead_capture_service] = (
        lambda: _build_dashboard_service(db_session)
    )
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_first_website_inquiry_sets_milestone(
    widget_milestone_client: TestClient,
    auth_headers: dict[str, str],
    company,
    db_session,
) -> None:
    response = widget_milestone_client.post(
        "/api/v1/public/widget/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "first-website-milestone",
            "message": "I need urgent roof repair tomorrow morning.",
        },
    )
    assert response.status_code == 200
    lead_id = response.json()["lead_id"]
    assert lead_id is not None

    activation_repository = CompanyActivationRepository(db_session)
    activation = activation_repository.get_by_company_id(company.id)
    assert activation is not None
    assert activation.first_website_inquiry_at is not None
    assert str(activation.first_website_inquiry_lead_id) == lead_id

    detail_response = widget_milestone_client.get(
        f"/api/v1/leads/{lead_id}",
        headers=auth_headers,
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["is_first_website_inquiry"] is True


def test_test_inquiry_does_not_set_milestone(
    dashboard_milestone_client: TestClient,
    auth_headers: dict[str, str],
    company,
    db_session,
) -> None:
    response = dashboard_milestone_client.post(
        "/api/v1/agents/lead/message",
        json={
            "conversation_id": "dashboard-test-milestone",
            "message": "I need urgent roof repair tomorrow morning.",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    lead_id = response.json()["lead_id"]
    assert lead_id is not None

    activation_repository = CompanyActivationRepository(db_session)
    activation = activation_repository.get_by_company_id(company.id)
    assert activation is None or activation.first_website_inquiry_at is None

    detail_response = dashboard_milestone_client.get(
        f"/api/v1/leads/{lead_id}",
        headers=auth_headers,
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["is_first_website_inquiry"] is False


def test_second_website_inquiry_does_not_overwrite_first_timestamp(
    db_session,
    auth_headers: dict[str, str],
    company,
) -> None:
    lead_repository = LeadRepository(db_session)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [_COMPLETE_WEBSITE_OUTPUT, _COMPLETE_WEBSITE_OUTPUT]
        ),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        activation_repository=CompanyActivationRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
        channel=ConversationChannel.WEB,
    )
    app.dependency_overrides[get_widget_lead_capture_service] = lambda: service
    client = TestClient(app)

    try:
        first_response = client.post(
            "/api/v1/public/widget/message",
            json={
                "company_slug": company.slug,
                "conversation_id": "first-website-conv",
                "message": "First website inquiry.",
            },
        )
        second_response = client.post(
            "/api/v1/public/widget/message",
            json={
                "company_slug": company.slug,
                "conversation_id": "second-website-conv",
                "message": "Second website inquiry.",
            },
        )
        assert first_response.status_code == 200
        assert second_response.status_code == 200

        activation_repository = CompanyActivationRepository(db_session)
        activation = activation_repository.get_by_company_id(company.id)
        assert activation is not None
        first_lead_id = first_response.json()["lead_id"]
        second_lead_id = second_response.json()["lead_id"]
        assert str(activation.first_website_inquiry_lead_id) == first_lead_id

        first_detail = client.get(
            f"/api/v1/leads/{first_lead_id}",
            headers=auth_headers,
        )
        second_detail = client.get(
            f"/api/v1/leads/{second_lead_id}",
            headers=auth_headers,
        )
        assert first_detail.json()["is_first_website_inquiry"] is True
        assert second_detail.json()["is_first_website_inquiry"] is False
    finally:
        app.dependency_overrides.clear()
