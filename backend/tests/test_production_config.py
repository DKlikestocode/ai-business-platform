import pytest
from fastapi.testclient import TestClient

from app.config import DEFAULT_JWT_SECRET, Settings, validate_production_settings
from app.main import create_app


def test_validate_production_settings_accepts_development() -> None:
    validate_production_settings(Settings(app_env="development"))


def test_validate_production_settings_rejects_default_jwt() -> None:
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        validate_production_settings(
            Settings(
                app_env="production",
                jwt_secret_key=DEFAULT_JWT_SECRET,
                openai_api_key="sk-test",
            )
        )


def test_validate_production_settings_rejects_short_jwt() -> None:
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        validate_production_settings(
            Settings(
                app_env="production",
                jwt_secret_key="too-short",
                openai_api_key="sk-test",
            )
        )


def test_validate_production_settings_requires_openai_key() -> None:
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        validate_production_settings(
            Settings(
                app_env="production",
                jwt_secret_key="a" * 32,
                openai_api_key="",
            )
        )


def test_openapi_disabled_in_production() -> None:
    settings = Settings(
        app_env="production",
        jwt_secret_key="a" * 32,
        openai_api_key="sk-test",
    )
    production_app = create_app(settings)
    client = TestClient(production_app)

    assert production_app.openapi_url is None
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_registration_disabled_in_production(dev_client: TestClient) -> None:
    from app.config import get_settings
    from app.main import app

    production_settings = Settings(
        app_env="production",
        jwt_secret_key="a" * 32,
        openai_api_key="sk-test",
    )
    app.dependency_overrides[get_settings] = lambda: production_settings
    try:
        response = dev_client.post(
            "/api/v1/companies",
            json={"name": "Blocked Co", "email": "blocked@example.com"},
        )
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_login_rate_limit_returns_429(dev_client: TestClient, auth_user) -> None:
    payload = {"email": auth_user.email, "password": "wrong-password"}

    for _ in range(10):
        response = dev_client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 401

    response = dev_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 429
