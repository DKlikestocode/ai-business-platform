import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.models.enums import UserRole
from app.main import app


@pytest.fixture
def settings_client() -> TestClient:
    return TestClient(app)


def test_get_company_settings_requires_authentication(settings_client: TestClient) -> None:
    response = settings_client.get("/api/v1/company/settings")

    assert response.status_code == 401


def test_get_company_settings_returns_current_company(
    settings_client: TestClient,
    company,
    auth_headers: dict[str, str],
) -> None:
    response = settings_client.get("/api/v1/company/settings", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == company.name
    assert body["slug"] == company.slug
    assert body["email"] == company.email
    assert body["phone"] == company.phone
    assert body["notification_email"] is None
    assert body["notify_on_new_lead"] is True
    assert body["notify_on_contactable_lead"] is True
    assert body["contactable_lead_notification_threshold"] == 50
    assert body["created_at"]


def test_patch_company_settings_updates_editable_fields(
    settings_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = settings_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={
            "name": "Updated Company Name",
            "email": "updated@example.com",
            "phone": "+49 30 123456",
            "notification_email": "alerts@example.com",
            "notify_on_new_lead": False,
            "notify_on_contactable_lead": True,
            "contactable_lead_notification_threshold": 60,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated Company Name"
    assert body["email"] == "updated@example.com"
    assert body["phone"] == "+49 30 123456"
    assert body["notification_email"] == "alerts@example.com"
    assert body["notify_on_new_lead"] is False
    assert body["notify_on_contactable_lead"] is True
    assert body["contactable_lead_notification_threshold"] == 60


def test_patch_company_settings_preserves_read_only_fields(
    settings_client: TestClient,
    company,
    auth_headers: dict[str, str],
) -> None:
    original_slug = company.slug
    original_created_at = company.created_at.isoformat()

    response = settings_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={"name": "Renamed Company"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == original_slug
    assert body["created_at"].startswith(original_created_at[:19])


def test_patch_company_settings_rejects_invalid_threshold(
    settings_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = settings_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={"contactable_lead_notification_threshold": 150},
    )

    assert response.status_code == 422


def test_company_settings_scoped_to_authenticated_tenant(
    settings_client: TestClient,
    user_repository,
    company_repository,
) -> None:
    suffix = uuid.uuid4().hex[:8]
    other_company = company_repository.create(
        name=f"Other Company {suffix}",
        email=f"other-{suffix}@example.com",
        slug=f"other-company-{suffix}",
    )
    other_user = user_repository.create(
        company_id=other_company.id,
        first_name="Other",
        last_name="User",
        email=f"other-user-{suffix}@example.com",
        password_hash=hash_password("secure-password"),
        role=UserRole.MEMBER,
    )
    login_response = settings_client.post(
        "/api/v1/auth/login",
        json={"email": other_user.email, "password": "secure-password"},
    )
    assert login_response.status_code == 200
    other_headers = {
        "Authorization": f"Bearer {login_response.json()['access_token']}",
    }

    response = settings_client.get("/api/v1/company/settings", headers=other_headers)

    assert response.status_code == 200
    assert response.json()["slug"] == other_company.slug
    assert response.json()["email"] == other_company.email
