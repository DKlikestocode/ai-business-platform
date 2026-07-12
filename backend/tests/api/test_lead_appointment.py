import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.models import (
    AppointmentConfirmationPreference,
    InquiryKind,
    LeadExtractedData,
    LeadStatus,
)
from app.agents.lead_agent.qualification import evaluate_qualification
from app.agents.lead_agent.repository import LeadRepository
from app.api.dependencies import get_notification_service
from app.core.security import hash_password
from app.db.models.company import Company
from app.db.models.enums import ConversationChannel, UserRole
from app.main import app
from app.services.notifications.interface import EmailMessage
from app.services.notifications.service import NotificationService


@dataclass
class MockEmailProvider:
    messages: list[EmailMessage] = field(default_factory=list)

    async def send_email(self, message: EmailMessage) -> None:
        self.messages.append(message)


@pytest.fixture
def dashboard_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def other_company_auth_headers(dev_client: TestClient, user_repository, company_repository):
    suffix = uuid.uuid4().hex[:8]
    other_company = company_repository.create(
        name=f"Appointment Other Co {suffix}",
        email=f"appt-other-{suffix}@example.com",
    )
    user = user_repository.create(
        company_id=other_company.id,
        first_name="Other",
        last_name="User",
        email=f"appt-other-user-{suffix}@example.com",
        password_hash=hash_password("secure-password"),
        role=UserRole.MEMBER,
    )
    response = dev_client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "secure-password"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def appointment_lead(lead_repository: LeadRepository, company: Company):
    data = LeadExtractedData(
        name="Anna Schmidt",
        phone="01701234567",
        email="anna@example.com",
        location="Berlin",
        postal_code="10115",
        service_requested="Heizungswartung",
        description="Jährliche Wartung",
        urgency="mittel",
        preferred_callback_time="Morgen Vormittag",
        inquiry_kind=InquiryKind.APPOINTMENT_CONSULTATION,
    )
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)
    return lead_repository.create(
        company_id=company.id,
        conversation_id=f"appt-conv-{uuid.uuid4().hex[:8]}",
        data=data,
        summary="Heizungswartung morgen vormittags",
        qualification=qualification,
    )


@pytest.fixture
def mock_notification_service(lead_repository: LeadRepository) -> NotificationService:
    return NotificationService(MockEmailProvider(), lead_repository)


@pytest.fixture
def dashboard_client_with_notifications(
    mock_notification_service: NotificationService,
) -> TestClient:
    app.dependency_overrides[get_notification_service] = lambda: mock_notification_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(get_notification_service, None)


def test_calendar_ics_requires_authentication(dashboard_client: TestClient) -> None:
    response = dashboard_client.get(f"/api/v1/leads/{uuid.uuid4()}/calendar.ics")
    assert response.status_code == 401


def test_calendar_ics_returns_attachment(
    dashboard_client: TestClient,
    appointment_lead,
    auth_headers: dict[str, str],
) -> None:
    response = dashboard_client.get(
        f"/api/v1/leads/{appointment_lead.id}/calendar.ics",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "text/calendar" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]
    body = response.text
    assert "BEGIN:VCALENDAR" in body
    assert "BEGIN:VEVENT" in body
    assert "Heizungswartung" in body
    assert "Morgen Vormittag" in body


def test_calendar_ics_tenant_isolation(
    dashboard_client: TestClient,
    appointment_lead,
    other_company_auth_headers: dict,
) -> None:
    response = dashboard_client.get(
        f"/api/v1/leads/{appointment_lead.id}/calendar.ics",
        headers=other_company_auth_headers,
    )
    assert response.status_code == 404


def test_appointment_confirmation_requires_authentication(dashboard_client: TestClient) -> None:
    response = dashboard_client.post(
        f"/api/v1/leads/{uuid.uuid4()}/appointment-confirmation",
        json={"channel": "email"},
    )
    assert response.status_code == 401


def test_appointment_confirmation_happy_path(
    dashboard_client_with_notifications: TestClient,
    appointment_lead,
    auth_headers: dict[str, str],
    mock_notification_service: NotificationService,
) -> None:
    provider = mock_notification_service._provider
    assert isinstance(provider, MockEmailProvider)

    response = dashboard_client_with_notifications.post(
        f"/api/v1/leads/{appointment_lead.id}/appointment-confirmation",
        json={"channel": "email"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sent"] is True
    assert body["appointment_confirmation_sent_at"] is not None
    assert len(provider.messages) == 1
    assert provider.messages[0].to == "anna@example.com"
    assert "Terminbestätigung" in provider.messages[0].subject


def test_appointment_confirmation_blocks_duplicate(
    dashboard_client_with_notifications: TestClient,
    appointment_lead,
    auth_headers: dict[str, str],
) -> None:
    first = dashboard_client_with_notifications.post(
        f"/api/v1/leads/{appointment_lead.id}/appointment-confirmation",
        json={"channel": "email"},
        headers=auth_headers,
    )
    assert first.status_code == 200

    second = dashboard_client_with_notifications.post(
        f"/api/v1/leads/{appointment_lead.id}/appointment-confirmation",
        json={"channel": "email"},
        headers=auth_headers,
    )
    assert second.status_code == 409


def test_appointment_confirmation_rejects_sms_channel(
    dashboard_client_with_notifications: TestClient,
    appointment_lead,
    auth_headers: dict[str, str],
) -> None:
    response = dashboard_client_with_notifications.post(
        f"/api/v1/leads/{appointment_lead.id}/appointment-confirmation",
        json={"channel": "sms"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "SMS" in response.json()["detail"]


def test_appointment_confirmation_missing_email(
    dashboard_client_with_notifications: TestClient,
    lead_repository: LeadRepository,
    company: Company,
    auth_headers: dict[str, str],
) -> None:
    data = LeadExtractedData(
        name="No Email",
        phone="01701234567",
        email=None,
        location="Berlin",
        postal_code="10115",
        service_requested="Service",
        description="Desc",
        urgency="mittel",
        preferred_callback_time="Morgen",
        inquiry_kind=InquiryKind.APPOINTMENT_CONSULTATION,
    )
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)
    lead = lead_repository.create(
        company_id=company.id,
        conversation_id=f"no-email-{uuid.uuid4().hex[:8]}",
        data=data,
        summary="No email lead",
        qualification=qualification,
    )

    response = dashboard_client_with_notifications.post(
        f"/api/v1/leads/{lead.id}/appointment-confirmation",
        json={"channel": "email"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_appointment_confirmation_tenant_isolation(
    dashboard_client_with_notifications: TestClient,
    appointment_lead,
    other_company_auth_headers: dict,
) -> None:
    response = dashboard_client_with_notifications.post(
        f"/api/v1/leads/{appointment_lead.id}/appointment-confirmation",
        json={"channel": "email"},
        headers=other_company_auth_headers,
    )
    assert response.status_code == 404


def test_get_lead_includes_appointment_fields(
    dashboard_client: TestClient,
    lead_repository: LeadRepository,
    company: Company,
    auth_headers: dict[str, str],
) -> None:
    data = LeadExtractedData(
        name="Termin Lead",
        phone="01701234567",
        email="termin@example.com",
        location="Berlin",
        postal_code="10115",
        service_requested="Beratung",
        description="Vor-Ort-Termin",
        urgency="mittel",
        preferred_callback_time="Freitag Nachmittag",
        inquiry_kind=InquiryKind.APPOINTMENT_CONSULTATION,
        appointment_confirmation_preference=AppointmentConfirmationPreference.EMAIL,
    )
    qualification = evaluate_qualification(data, channel=ConversationChannel.WEB)
    lead = lead_repository.create(
        company_id=company.id,
        conversation_id=f"fields-{uuid.uuid4().hex[:8]}",
        data=data,
        summary="Beratung",
        qualification=qualification,
    )

    response = dashboard_client.get(
        f"/api/v1/leads/{lead.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["appointment_confirmation_preference"] == "email"
    assert "appointment_confirmation_sent_at" in body
