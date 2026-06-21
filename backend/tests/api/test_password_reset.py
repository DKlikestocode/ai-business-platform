import pytest
from fastapi.testclient import TestClient

from app.core.security import verify_password
from app.db.models.password_reset_token import PasswordResetToken
from app.main import app
from app.repositories.password_reset_repository import PasswordResetRepository


@pytest.fixture
def auth_client() -> TestClient:
    return TestClient(app)


def test_forgot_password_returns_204_even_for_unknown_email(
    auth_client: TestClient,
) -> None:
    response = auth_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "missing-user@example.com"},
    )

    assert response.status_code == 204


def test_forgot_password_creates_reset_token(
    auth_client: TestClient,
    auth_user,
    db_session,
) -> None:
    response = auth_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": auth_user.email},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dev_reset_url"]
    assert "token=" in body["dev_reset_url"]
    token = (
        db_session.query(PasswordResetToken)
        .filter(PasswordResetToken.user_id == auth_user.id)
        .one()
    )
    assert token.used_at is None


def test_forgot_password_is_case_insensitive_for_email(
    auth_client: TestClient,
    auth_user,
    db_session,
) -> None:
    response = auth_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": auth_user.email.upper()},
    )

    assert response.status_code == 200
    assert (
        db_session.query(PasswordResetToken)
        .filter(PasswordResetToken.user_id == auth_user.id)
        .count()
        == 1
    )


def test_reset_password_updates_password(
    auth_client: TestClient,
    auth_user,
    user_repository,
    db_session,
) -> None:
    repository = PasswordResetRepository(db_session)
    _, raw_token = repository.create_token(user_id=auth_user.id)

    response = auth_client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "password": "new-secure-password"},
    )

    assert response.status_code == 204
    updated_user = user_repository.get_by_email(auth_user.email)
    assert updated_user is not None
    assert verify_password("new-secure-password", updated_user.password_hash)
    assert not verify_password("secure-password", updated_user.password_hash)


def test_reset_password_rejects_invalid_token(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalid-token-value", "password": "new-secure-password"},
    )

    assert response.status_code == 400
