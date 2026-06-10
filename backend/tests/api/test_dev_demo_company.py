from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app
import pytest


def test_bootstrap_demo_company_is_idempotent(dev_client: TestClient) -> None:
    first = dev_client.post("/api/v1/dev/demo-company")
    second = dev_client.post("/api/v1/dev/demo-company")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["slug"] == "demo-company"
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["name"] == "Demo Company"


def test_bootstrap_demo_company_disabled_outside_development(
    dev_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()

    production_settings = Settings(app_env="production")
    app.dependency_overrides[get_settings] = lambda: production_settings
    try:
        response = dev_client.post("/api/v1/dev/demo-company")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
