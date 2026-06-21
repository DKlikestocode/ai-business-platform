import uuid

import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.repository import LeadRepository
from app.api.dependencies import get_notification_service
from app.main import app
from app.services.notifications.service import NotificationService
from tests.services.test_notification_service import MockEmailProvider


@pytest.fixture
def settings_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def mock_notification_provider() -> MockEmailProvider:
    return MockEmailProvider()


@pytest.fixture
def mock_notification_service(
    lead_repository: LeadRepository,
    mock_notification_provider: MockEmailProvider,
) -> NotificationService:
    return NotificationService(mock_notification_provider, lead_repository)


@pytest.fixture
def notification_client(
    settings_client: TestClient,
    mock_notification_service: NotificationService,
) -> TestClient:
    app.dependency_overrides[get_notification_service] = lambda: mock_notification_service
    yield settings_client
    app.dependency_overrides.clear()


def test_test_notification_requires_authentication(
    notification_client: TestClient,
) -> None:
    response = notification_client.post("/api/v1/company/settings/test-notification")

    assert response.status_code == 401


def test_test_notification_missing_notification_email_returns_422(
    notification_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = notification_client.post(
        "/api/v1/company/settings/test-notification",
        headers=auth_headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "No notification email configured."


def test_test_notification_sends_to_company_notification_email(
    notification_client: TestClient,
    auth_headers: dict[str, str],
    mock_notification_provider: MockEmailProvider,
) -> None:
    notification_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={"notification_email": "alerts@example.com"},
    )

    response = notification_client.post(
        "/api/v1/company/settings/test-notification",
        headers=auth_headers,
    )

    assert response.status_code == 204
    assert len(mock_notification_provider.messages) == 1
    message = mock_notification_provider.messages[0]
    assert message.to == "alerts@example.com"
    assert message.subject == "Test: Neue Anfrage über Ihren Website-Chat"
    assert "Test-E-Mail" in message.body
    assert "Anfrage" in message.body
    assert "Lead" not in message.body


def test_test_notification_ignores_arbitrary_recipient_in_body(
    notification_client: TestClient,
    auth_headers: dict[str, str],
    mock_notification_provider: MockEmailProvider,
) -> None:
    notification_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={"notification_email": "alerts@example.com"},
    )

    response = notification_client.post(
        "/api/v1/company/settings/test-notification",
        headers=auth_headers,
        json={"to": "evil@example.com", "email": "evil@example.com"},
    )

    assert response.status_code == 204
    assert mock_notification_provider.messages[0].to == "alerts@example.com"


def test_test_notification_does_not_create_lead(
    notification_client: TestClient,
    auth_headers: dict[str, str],
    lead_repository: LeadRepository,
    company,
) -> None:
    notification_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={"notification_email": "alerts@example.com"},
    )
    _, total_before = lead_repository.list_leads(
        page=1,
        page_size=100,
        company_id=company.id,
    )

    response = notification_client.post(
        "/api/v1/company/settings/test-notification",
        headers=auth_headers,
    )

    assert response.status_code == 204
    _, total_after = lead_repository.list_leads(
        page=1,
        page_size=100,
        company_id=company.id,
    )
    assert total_after == total_before


def test_test_notification_scoped_to_authenticated_tenant(
    notification_client: TestClient,
    company_repository,
    user_repository,
    mock_notification_provider: MockEmailProvider,
) -> None:
    from app.core.security import hash_password
    from app.db.models.enums import UserRole

    suffix = uuid.uuid4().hex[:8]
    other_company = company_repository.create(
        name=f"Other Company {suffix}",
        email=f"other-{suffix}@example.com",
        slug=f"other-company-{suffix}",
    )
    company_repository.update_settings(
        other_company,
        notification_email=f"other-alerts-{suffix}@example.com",
    )
    other_user = user_repository.create(
        company_id=other_company.id,
        first_name="Other",
        last_name="User",
        email=f"other-user-{suffix}@example.com",
        password_hash=hash_password("secure-password"),
        role=UserRole.MEMBER,
    )
    login_response = notification_client.post(
        "/api/v1/auth/login",
        json={"email": other_user.email, "password": "secure-password"},
    )
    other_headers = {
        "Authorization": f"Bearer {login_response.json()['access_token']}",
    }

    response = notification_client.post(
        "/api/v1/company/settings/test-notification",
        headers=other_headers,
    )

    assert response.status_code == 204
    assert len(mock_notification_provider.messages) == 1
    assert (
        mock_notification_provider.messages[0].to
        == f"other-alerts-{suffix}@example.com"
    )
