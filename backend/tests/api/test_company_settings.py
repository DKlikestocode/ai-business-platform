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
    assert body["notification_min_urgency"] == "medium"
    assert body["service_area_center"] is None
    assert body["service_radius_km"] is None
    assert body["trade"] is None
    assert body["email_delivery_provider"] == "logging"
    assert body["email_delivery_ready"] is True
    assert body["email_delivery_sends_real_email"] is False
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
            "notification_min_urgency": "low",
            "service_area_center": "München",
            "service_radius_km": 25,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated Company Name"
    assert body["email"] == "updated@example.com"
    assert body["phone"] == "+49 30 123456"
    assert body["notification_email"] == "alerts@example.com"
    assert body["notification_min_urgency"] == "low"
    assert body["service_area_center"] == "München"
    assert body["service_radius_km"] == 25


def test_patch_company_settings_updates_trade(
    settings_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = settings_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={"trade": "skh"},
    )

    assert response.status_code == 200
    assert response.json()["trade"] == "skh"


def test_patch_company_settings_rejects_invalid_trade(
    settings_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = settings_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={"trade": "invalid"},
    )

    assert response.status_code == 422


def test_patch_company_settings_resolves_service_area_coordinates_from_plz(
    settings_client: TestClient,
    company,
    db_session,
    auth_headers: dict[str, str],
) -> None:
    response = settings_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={
            "service_area_center": "80331 München",
            "service_radius_km": 30,
        },
    )

    assert response.status_code == 200
    db_session.refresh(company)
    assert company.service_area_latitude is not None
    assert company.service_area_longitude is not None
    assert 47 < company.service_area_latitude < 49
    assert 10 < company.service_area_longitude < 12


def test_patch_company_settings_rejects_invalid_notification_min_urgency(
    settings_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = settings_client.patch(
        "/api/v1/company/settings",
        headers=auth_headers,
        json={"notification_min_urgency": "urgent"},
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
