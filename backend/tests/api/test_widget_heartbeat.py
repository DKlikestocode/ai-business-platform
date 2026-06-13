import uuid
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.company_activation_repository import CompanyActivationRepository

HEARTBEAT_ORIGIN = "https://www.customer-example.de"
GENERIC_ERROR = "Invalid widget credentials."


@pytest.fixture
def heartbeat_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def company_activation(db_session, company):
    repository = CompanyActivationRepository(db_session)
    return repository.get_or_create(company.id)


def _heartbeat_payload(
    company,
    install_token: str,
    *,
    page_origin: str = HEARTBEAT_ORIGIN,
) -> dict[str, str]:
    return {
        "company_slug": company.slug,
        "install_token": install_token,
        "page_origin": page_origin,
    }


def test_widget_heartbeat_marks_activation_live(
    heartbeat_client: TestClient,
    company,
    company_activation,
    db_session,
) -> None:
    first_seen = datetime(2025, 6, 1, 10, 0, 0, tzinfo=UTC)
    payload = _heartbeat_payload(company, company_activation.install_token)

    with patch("app.repositories.company_activation_repository.datetime") as mock_dt:
        mock_dt.now.return_value = first_seen
        mock_dt.UTC = UTC
        response = heartbeat_client.post(
            "/api/v1/public/widget/heartbeat",
            json=payload,
        )

    assert response.status_code == 204
    assert response.content == b""

    db_session.expire_all()
    repository = CompanyActivationRepository(db_session)
    activation = repository.get_by_company_id(company.id)
    assert activation is not None
    assert activation.status == "live"
    assert activation.widget_live_at == first_seen
    assert activation.widget_last_seen_at == first_seen
    assert activation.widget_last_origin == HEARTBEAT_ORIGIN


def test_widget_heartbeat_invalid_token_rejected_generically(
    heartbeat_client: TestClient,
    company,
    company_activation,
) -> None:
    response = heartbeat_client.post(
        "/api/v1/public/widget/heartbeat",
        json=_heartbeat_payload(company, "wrong-token"),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == GENERIC_ERROR
    assert company.slug not in response.json()["detail"]


def test_widget_heartbeat_missing_tenant_rejected_generically(
    heartbeat_client: TestClient,
    company_activation,
) -> None:
    response = heartbeat_client.post(
        "/api/v1/public/widget/heartbeat",
        json={
            "company_slug": "missing-company-slug",
            "install_token": company_activation.install_token,
            "page_origin": HEARTBEAT_ORIGIN,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == GENERIC_ERROR
    assert "missing-company-slug" not in response.json()["detail"]


def test_widget_heartbeat_invalid_token_matches_missing_tenant_response(
    heartbeat_client: TestClient,
    company,
    company_activation,
) -> None:
    missing_tenant = heartbeat_client.post(
        "/api/v1/public/widget/heartbeat",
        json={
            "company_slug": "missing-company-slug",
            "install_token": "any-token",
            "page_origin": HEARTBEAT_ORIGIN,
        },
    )
    invalid_token = heartbeat_client.post(
        "/api/v1/public/widget/heartbeat",
        json=_heartbeat_payload(company, "wrong-token"),
    )

    assert missing_tenant.status_code == 404
    assert invalid_token.status_code == 404
    assert missing_tenant.json() == invalid_token.json()


def test_widget_heartbeat_is_idempotent_and_preserves_first_live_at(
    heartbeat_client: TestClient,
    company,
    company_activation,
    db_session,
) -> None:
    first_seen = datetime(2025, 6, 1, 10, 0, 0, tzinfo=UTC)
    second_seen = datetime(2025, 6, 1, 10, 5, 0, tzinfo=UTC)
    payload = _heartbeat_payload(company, company_activation.install_token)

    with patch("app.repositories.company_activation_repository.datetime") as mock_dt:
        mock_dt.now.return_value = first_seen
        mock_dt.UTC = UTC
        first_response = heartbeat_client.post(
            "/api/v1/public/widget/heartbeat",
            json=payload,
        )

    assert first_response.status_code == 204

    with patch("app.repositories.company_activation_repository.datetime") as mock_dt:
        mock_dt.now.return_value = second_seen
        mock_dt.UTC = UTC
        second_response = heartbeat_client.post(
            "/api/v1/public/widget/heartbeat",
            json=payload,
        )

    assert second_response.status_code == 204

    db_session.expire_all()
    repository = CompanyActivationRepository(db_session)
    activation = repository.get_by_company_id(company.id)
    assert activation is not None
    assert activation.widget_live_at == first_seen
    assert activation.widget_last_seen_at == second_seen


def test_widget_heartbeat_rejects_internal_origin(
    heartbeat_client: TestClient,
    company,
    company_activation,
    db_session,
) -> None:
    response = heartbeat_client.post(
        "/api/v1/public/widget/heartbeat",
        json=_heartbeat_payload(
            company,
            company_activation.install_token,
            page_origin="http://localhost:3000",
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == GENERIC_ERROR

    repository = CompanyActivationRepository(db_session)
    activation = repository.get_by_company_id(company.id)
    assert activation is not None
    assert activation.status == "awaiting_widget"
    assert activation.widget_live_at is None


def test_widget_heartbeat_without_activation_row_rejects_generically(
    heartbeat_client: TestClient,
    company,
    db_session,
) -> None:
    repository = CompanyActivationRepository(db_session)
    assert repository.get_by_company_id(company.id) is None

    response = heartbeat_client.post(
        "/api/v1/public/widget/heartbeat",
        json=_heartbeat_payload(company, "any-token"),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == GENERIC_ERROR
    assert company.slug not in response.json()["detail"]
    assert repository.get_by_company_id(company.id) is None


def test_widget_heartbeat_invalid_token_does_not_create_activation_row(
    heartbeat_client: TestClient,
    company,
    company_activation,
    db_session,
) -> None:
    repository = CompanyActivationRepository(db_session)
    before = repository.get_by_company_id(company.id)
    assert before is not None
    assert before.status == "awaiting_widget"

    response = heartbeat_client.post(
        "/api/v1/public/widget/heartbeat",
        json=_heartbeat_payload(company, "wrong-token"),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == GENERIC_ERROR

    db_session.expire_all()
    after = repository.get_by_company_id(company.id)
    assert after is not None
    assert after.company_id == before.company_id
    assert after.install_token == before.install_token
    assert after.status == "awaiting_widget"
    assert after.widget_live_at is None


def test_widget_heartbeat_does_not_leak_other_tenant_slug(
    heartbeat_client: TestClient,
    company_repository,
    db_session,
) -> None:
    suffix = uuid.uuid4().hex[:8]
    other_company = company_repository.create(
        name=f"Heartbeat Other {suffix}",
        email=f"heartbeat-other-{suffix}@example.com",
    )
    other_activation = CompanyActivationRepository(db_session).get_or_create(
        other_company.id,
    )

    response = heartbeat_client.post(
        "/api/v1/public/widget/heartbeat",
        json=_heartbeat_payload(other_company, "wrong-token"),
    )

    assert response.status_code == 404
    assert other_company.slug not in response.json()["detail"]
    assert other_activation.install_token not in response.json()["detail"]
