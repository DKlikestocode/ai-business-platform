from collections.abc import Mapping
from typing import Any

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.api.dependencies import (
    get_resend_received_email_client,
    get_resend_webhook_verifier,
)
from app.api.routes.webhooks import MAX_WEBHOOK_BYTES, _read_limited_body
from app.config import Settings, get_settings
from app.main import app
from app.repositories.intake_repository import IntakeRepository
from tests.intake.conftest import FIXTURE_ROOT


class AcceptingVerifier:
    def __init__(self, company_slug: str) -> None:
        self.company_slug = company_slug

    def verify(
        self,
        payload: bytes,
        headers: Mapping[str, str],
    ) -> dict[str, Any]:
        return {
            "type": "email.received",
            "data": {
                "email_id": "resend-email-1",
                "to": [f"Test <{self.company_slug}@inbound.example.test>"],
            },
        }


class StaticRawEmailClient:
    def __init__(self, raw_message: bytes) -> None:
        self.raw_message = raw_message

    async def retrieve_raw_message(self, email_id: str) -> bytes:
        assert email_id == "resend-email-1"
        return self.raw_message


@pytest.mark.asyncio
async def test_rejects_oversized_webhook_before_reading_body() -> None:
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/webhooks/resend",
            "headers": [
                (b"content-length", str(MAX_WEBHOOK_BYTES + 1).encode("ascii"))
            ],
        }
    )

    with pytest.raises(HTTPException) as exc_info:
        await _read_limited_body(request)

    assert exc_info.value.status_code == 413


def test_resend_webhook_stores_raw_email_once(
    dev_client: TestClient,
    company,
    intake_repository: IntakeRepository,
) -> None:
    raw_message = (
        FIXTURE_ROOT / "cases" / "case_002" / "inquiry.eml"
    ).read_bytes()
    settings = Settings(
        intake_email_enabled=True,
        resend_inbound_domain="inbound.example.test",
        resend_api_key="test-key",
        resend_webhook_secret="test-secret",
    )
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_resend_webhook_verifier] = lambda: (
        AcceptingVerifier(company.slug)
    )
    app.dependency_overrides[get_resend_received_email_client] = lambda: (
        StaticRawEmailClient(raw_message)
    )
    try:
        headers = {"svix-id": "event-1"}
        first = dev_client.post("/api/v1/webhooks/resend", content=b"{}", headers=headers)
        second = dev_client.post("/api/v1/webhooks/resend", content=b"{}", headers=headers)
    finally:
        app.dependency_overrides.clear()

    assert first.status_code == 202
    assert first.json()["created"] is True
    assert second.status_code == 202
    assert second.json()["created"] is False
    item = intake_repository.get_by_id(
        first.json()["intake_item_id"],
        company_id=company.id,
    )
    assert item is not None
    document = intake_repository.get_document(item.id, company_id=company.id)
    assert document is not None
    assert document.content == raw_message
