import pytest
from fastapi import HTTPException

from app.config import Settings
from app.services.voice.webhook_auth import require_vapi_webhook_secret


def test_webhook_secret_skipped_when_not_configured() -> None:
    settings = Settings(vapi_webhook_secret="")
    require_vapi_webhook_secret(None, settings)


def test_webhook_secret_rejects_missing_header() -> None:
    settings = Settings(vapi_webhook_secret="pilot-secret")
    with pytest.raises(HTTPException) as exc_info:
        require_vapi_webhook_secret(None, settings)
    assert exc_info.value.status_code == 401


def test_webhook_secret_rejects_wrong_header() -> None:
    settings = Settings(vapi_webhook_secret="pilot-secret")
    with pytest.raises(HTTPException) as exc_info:
        require_vapi_webhook_secret("wrong", settings)
    assert exc_info.value.status_code == 401


def test_webhook_secret_accepts_matching_header() -> None:
    settings = Settings(vapi_webhook_secret="pilot-secret")
    require_vapi_webhook_secret("pilot-secret", settings)
