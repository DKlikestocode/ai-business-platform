import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.models.enums import UserRole
from app.main import app
from app.repositories.company_activation_repository import CompanyActivationRepository


@pytest.fixture
def activation_client() -> TestClient:
    return TestClient(app)


def test_get_activation_requires_authentication(
    activation_client: TestClient,
) -> None:
    response = activation_client.get("/api/v1/company/activation")

    assert response.status_code == 401


def test_get_activation_lazy_creates_row(
    activation_client: TestClient,
    company,
    auth_headers: dict[str, str],
    db_session,
) -> None:
    repository = CompanyActivationRepository(db_session)
    assert repository.get_by_company_id(company.id) is None

    response = activation_client.get(
        "/api/v1/company/activation",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["notification_configured"] is True
    assert body["status"] == "awaiting_widget"
    assert body["website_url"] is None
    assert body["install"]["company_slug"] == company.slug
    assert "data-install-token=" in body["install"]["embed_snippet"]
    assert company.slug in body["install"]["embed_snippet"]

    created = repository.get_by_company_id(company.id)
    assert created is not None
    assert created.install_token


def test_install_token_stable_across_reads(
    activation_client: TestClient,
    auth_headers: dict[str, str],
    db_session,
    company,
) -> None:
    first = activation_client.get(
        "/api/v1/company/activation",
        headers=auth_headers,
    )
    second = activation_client.get(
        "/api/v1/company/activation",
        headers=auth_headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert (
        first.json()["install"]["embed_snippet"]
        == second.json()["install"]["embed_snippet"]
    )

    repository = CompanyActivationRepository(db_session)
    activation = repository.get_by_company_id(company.id)
    assert activation is not None
    assert activation.install_token in first.json()["install"]["embed_snippet"]


def test_notification_configured_derived_from_company_email(
    activation_client: TestClient,
    auth_headers: dict[str, str],
    company,
) -> None:
    response = activation_client.get(
        "/api/v1/company/activation",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["notification_configured"] is True
    assert body["status"] == "awaiting_widget"


def test_patch_activation_updates_website_url(
    activation_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    activation_client.get("/api/v1/company/activation", headers=auth_headers)

    response = activation_client.patch(
        "/api/v1/company/activation",
        headers=auth_headers,
        json={"website_url": "https://www.example.de"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["website_url"] == "https://www.example.de"


def test_activation_scoped_to_authenticated_tenant(
    activation_client: TestClient,
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
    login_response = activation_client.post(
        "/api/v1/auth/login",
        json={"email": other_user.email, "password": "secure-password"},
    )
    assert login_response.status_code == 200
    other_headers = {
        "Authorization": f"Bearer {login_response.json()['access_token']}",
    }

    response = activation_client.get(
        "/api/v1/company/activation",
        headers=other_headers,
    )

    assert response.status_code == 200
    assert response.json()["install"]["company_slug"] == other_company.slug
