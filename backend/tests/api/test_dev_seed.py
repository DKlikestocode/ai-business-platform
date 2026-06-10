import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app


@pytest.fixture
def dev_client(db_session) -> TestClient:
    return TestClient(app)


def test_seed_demo_data_creates_or_skips_existing(dev_client: TestClient) -> None:
    response = dev_client.post("/api/v1/dev/seed-demo-data")

    assert response.status_code == 200
    body = response.json()
    assert body["created"] + body["skipped"] == 5
    assert body["message"]
    if body["created"] > 0:
        assert len(body["lead_ids"]) == body["created"]


def test_seed_demo_data_is_idempotent(dev_client: TestClient) -> None:
    first = dev_client.post("/api/v1/dev/seed-demo-data")
    second = dev_client.post("/api/v1/dev/seed-demo-data")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["created"] == 0
    assert second.json()["skipped"] == 5


def test_seed_demo_data_disabled_outside_development(
    dev_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()

    production_settings = Settings(app_env="production")
    app.dependency_overrides[get_settings] = lambda: production_settings
    try:
        response = dev_client.post("/api/v1/dev/seed-demo-data")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
