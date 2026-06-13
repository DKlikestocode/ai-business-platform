from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db.models.company_activation import CompanyActivation
from app.db.models.enums import ActivationStatus
from app.main import app
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.services.activation.service import ActivationService

HEARTBEAT_ORIGIN = "https://www.customer-example.de"


def _build_service(*, widget_stale_after_hours: int = 168) -> ActivationService:
    return ActivationService(
        MagicMock(),
        MagicMock(),
        public_api_base_url="http://localhost:8000",
        widget_stale_after_hours=widget_stale_after_hours,
    )


def _activation(
    *,
    status: ActivationStatus = ActivationStatus.LIVE,
    last_seen: datetime | None = None,
) -> CompanyActivation:
    activation = CompanyActivation(
        company_id=uuid4(),
        install_token="token",
        status=status.value,
    )
    activation.widget_last_seen_at = last_seen
    return activation


def test_live_with_recent_widget_last_seen_returns_live() -> None:
    service = _build_service()
    company = MagicMock()
    company.notification_email = "alerts@example.com"
    activation = _activation(
        last_seen=datetime.now(UTC) - timedelta(hours=1),
    )

    assert service._effective_status(company, activation) == ActivationStatus.LIVE


def test_live_with_old_widget_last_seen_returns_stale() -> None:
    service = _build_service(widget_stale_after_hours=168)
    company = MagicMock()
    company.notification_email = "alerts@example.com"
    activation = _activation(
        last_seen=datetime.now(UTC) - timedelta(hours=200),
    )

    assert service._effective_status(company, activation) == ActivationStatus.STALE


def test_missing_widget_last_seen_does_not_mark_stale() -> None:
    service = _build_service()
    company = MagicMock()
    company.notification_email = "alerts@example.com"
    activation = _activation(last_seen=None)

    assert service._effective_status(company, activation) == ActivationStatus.LIVE


@pytest.fixture
def stale_client() -> TestClient:
    return TestClient(app)


def test_get_activation_returns_stale_for_old_live_heartbeat(
    stale_client: TestClient,
    auth_headers: dict[str, str],
    company,
    db_session,
) -> None:
    company_repository = CompanyRepository(db_session)
    company_repository.update_settings(
        company,
        notification_email="alerts@example.com",
    )

    activation_repository = CompanyActivationRepository(db_session)
    activation = activation_repository.get_or_create(company.id)
    activation.status = ActivationStatus.LIVE.value
    activation.widget_live_at = datetime.now(UTC) - timedelta(days=10)
    activation.widget_last_seen_at = datetime.now(UTC) - timedelta(days=10)
    activation.widget_last_origin = HEARTBEAT_ORIGIN
    db_session.commit()

    response = stale_client.get(
        "/api/v1/company/activation",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "stale"
    assert body["widget_last_origin"] == HEARTBEAT_ORIGIN
    assert body["widget_last_seen_at"] is not None


def test_recent_heartbeat_restores_live_from_stale_effective_status(
    stale_client: TestClient,
    auth_headers: dict[str, str],
    company,
    db_session,
) -> None:
    company_repository = CompanyRepository(db_session)
    company_repository.update_settings(
        company,
        notification_email="alerts@example.com",
    )

    activation_repository = CompanyActivationRepository(db_session)
    activation = activation_repository.get_or_create(company.id)
    activation.status = ActivationStatus.LIVE.value
    activation.widget_live_at = datetime.now(UTC) - timedelta(days=10)
    activation.widget_last_seen_at = datetime.now(UTC) - timedelta(days=10)
    activation.widget_last_origin = HEARTBEAT_ORIGIN
    db_session.commit()

    stale_response = stale_client.get(
        "/api/v1/company/activation",
        headers=auth_headers,
    )
    assert stale_response.status_code == 200
    assert stale_response.json()["status"] == "stale"

    recent_seen = datetime.now(UTC)
    with patch("app.repositories.company_activation_repository.datetime") as mock_dt:
        mock_dt.now.return_value = recent_seen
        mock_dt.UTC = UTC
        heartbeat_response = stale_client.post(
            "/api/v1/public/widget/heartbeat",
            json={
                "company_slug": company.slug,
                "install_token": activation.install_token,
                "page_origin": HEARTBEAT_ORIGIN,
            },
        )

    assert heartbeat_response.status_code == 204

    live_response = stale_client.get(
        "/api/v1/company/activation",
        headers=auth_headers,
    )
    assert live_response.status_code == 200
    assert live_response.json()["status"] == "live"
