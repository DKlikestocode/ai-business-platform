import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.models import LeadCaptureLLMOutput, LeadExtractedData
from app.agents.lead_agent.repository import LeadRepository
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import get_lead_capture_service, get_widget_lead_capture_service
from app.db.models.enums import ConversationChannel
from app.main import app
from app.repositories.company_repository import CompanyRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.notifications.service import NotificationService
from tests.agents.lead_agent.conftest import MockLeadExtractionClient
from tests.services.test_notification_service import MockEmailProvider


def _build_widget_service(db_session) -> LeadCaptureService:
    lead_repository = LeadRepository(db_session)
    return LeadCaptureService(
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
        channel=ConversationChannel.WEB,
    )


def _build_dashboard_service(db_session) -> LeadCaptureService:
    lead_repository = LeadRepository(db_session)
    return LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [
                LeadCaptureLLMOutput(
                    reply="Thanks! What service do you need?",
                    name="Dashboard User",
                    phone="555-0100",
                ),
            ]
        ),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
        channel=ConversationChannel.DASHBOARD,
    )


@pytest.fixture
def widget_client(db_session) -> TestClient:
    app.dependency_overrides[get_widget_lead_capture_service] = (
        lambda: _build_widget_service(db_session)
    )
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def dashboard_message_client(db_session) -> TestClient:
    app.dependency_overrides[get_lead_capture_service] = (
        lambda: _build_dashboard_service(db_session)
    )
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_public_widget_message_persists_website_channel(
    widget_client: TestClient,
    company,
    db_session,
) -> None:
    response = widget_client.post(
        "/api/v1/public/widget/message",
        json={
            "company_slug": company.slug,
            "conversation_id": "widget-channel-conv",
            "message": "Hi from the website widget.",
        },
    )

    assert response.status_code == 200

    conversation_repository = ConversationRepository(db_session)
    conversation = conversation_repository.get_by_external_id(
        company_id=company.id,
        external_id="widget-channel-conv",
    )
    assert conversation is not None
    assert conversation.channel == ConversationChannel.WEB.value


def test_dashboard_test_message_persists_dashboard_channel(
    dashboard_message_client: TestClient,
    auth_headers: dict[str, str],
    company,
    db_session,
) -> None:
    response = dashboard_message_client.post(
        "/api/v1/agents/lead/message",
        json={
            "conversation_id": "dashboard-test-conv",
            "message": "Hi from dashboard test chat.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    conversation_repository = ConversationRepository(db_session)
    conversation = conversation_repository.get_by_external_id(
        company_id=company.id,
        external_id="dashboard-test-conv",
    )
    assert conversation is not None
    assert conversation.channel == ConversationChannel.DASHBOARD.value


def test_lead_list_and_detail_return_source_from_conversation_channel(
    dashboard_message_client: TestClient,
    auth_headers: dict[str, str],
    company,
    db_session,
) -> None:
    conversation_repository = ConversationRepository(db_session)
    lead_repository = LeadRepository(db_session)

    conversation_repository.create(
        company_id=company.id,
        external_id="website-source-conv",
        channel=ConversationChannel.WEB,
    )
    conversation_repository.create(
        company_id=company.id,
        external_id="dashboard-source-conv",
        channel=ConversationChannel.DASHBOARD,
    )

    website_lead = lead_repository.create(
        company_id=company.id,
        conversation_id="website-source-conv",
        data=LeadExtractedData(
            name="Website Lead",
            phone="555-0200",
            location="Berlin",
            service_requested="Heating",
            description="No heat",
            urgency="high",
            preferred_callback_time="Today",
        ),
        summary="Website lead",
    )
    test_lead = lead_repository.create(
        company_id=company.id,
        conversation_id="dashboard-source-conv",
        data=LeadExtractedData(
            name="Test Lead",
            phone="555-0300",
            location="Berlin",
            service_requested="Plumbing",
            description="Leak",
            urgency="medium",
            preferred_callback_time="Tomorrow",
        ),
        summary="Test lead",
    )

    list_response = dashboard_message_client.get(
        "/api/v1/leads?page=1&page_size=20",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    items = {item["conversation_id"]: item for item in list_response.json()["items"]}

    assert items["website-source-conv"]["source"] == "website"
    assert items["dashboard-source-conv"]["source"] == "test"

    website_detail = dashboard_message_client.get(
        f"/api/v1/leads/{website_lead.id}",
        headers=auth_headers,
    )
    test_detail = dashboard_message_client.get(
        f"/api/v1/leads/{test_lead.id}",
        headers=auth_headers,
    )

    assert website_detail.status_code == 200
    assert website_detail.json()["source"] == "website"
    assert test_detail.status_code == 200
    assert test_detail.json()["source"] == "test"


def test_reused_demo_chat_conversation_upgrades_to_dashboard_channel_and_test_source(
    db_session,
    company,
    auth_headers: dict[str, str],
) -> None:
    conversation_repository = ConversationRepository(db_session)
    conversation_repository.create(
        company_id=company.id,
        external_id="demo-chat-001",
        channel=ConversationChannel.WEB,
    )

    lead_repository = LeadRepository(db_session)
    complete_client = TestClient(app)
    service = LeadCaptureService(
        agent=LeadCaptureAgent(),
        conversation_repository=ConversationRepository(db_session),
        extraction_client=MockLeadExtractionClient(
            [
                LeadCaptureLLMOutput(
                    reply="Thanks, we have everything we need.",
                    summary="Reused demo chat lead",
                    name="Reuse User",
                    phone="555-0400",
                    location="Berlin",
                    service_requested="Electrical",
                    description="Outlet issue",
                    urgency="medium",
                    preferred_callback_time="Tomorrow",
                ),
            ]
        ),
        repository=lead_repository,
        company_repository=CompanyRepository(db_session),
        notification_service=NotificationService(MockEmailProvider(), lead_repository),
        channel=ConversationChannel.DASHBOARD,
    )
    app.dependency_overrides[get_lead_capture_service] = lambda: service

    try:
        message_response = complete_client.post(
            "/api/v1/agents/lead/message",
            json={
                "conversation_id": "demo-chat-001",
                "message": "I need an electrician tomorrow.",
            },
            headers=auth_headers,
        )
        assert message_response.status_code == 200
        assert message_response.json()["lead_id"] is not None

        db_session.expire_all()
        conversation = conversation_repository.get_by_external_id(
            company_id=company.id,
            external_id="demo-chat-001",
        )
        assert conversation is not None
        assert conversation.channel == ConversationChannel.DASHBOARD.value

        lead_id = message_response.json()["lead_id"]
        detail_response = complete_client.get(
            f"/api/v1/leads/{lead_id}",
            headers=auth_headers,
        )
        assert detail_response.status_code == 200
        assert detail_response.json()["source"] == "test"
    finally:
        app.dependency_overrides.clear()
