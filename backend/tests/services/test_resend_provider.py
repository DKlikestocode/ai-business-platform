from dataclasses import dataclass, field
from typing import Any

import httpx
import pytest

from app.config import Settings
from app.services.notifications.interface import EmailMessage
from app.services.notifications.resend_provider import RESEND_API_URL, ResendEmailProvider


def _response(status_code: int, *, json: dict[str, Any] | None = None) -> httpx.Response:
    request = httpx.Request("POST", RESEND_API_URL)
    return httpx.Response(status_code, json=json, request=request)


@dataclass
class MockResendHttpClient:
    responses: list[httpx.Response] = field(default_factory=list)
    requests: list[dict[str, Any]] = field(default_factory=list)

    async def post(
        self,
        url: str,
        *,
        json: dict[str, Any],
        headers: dict[str, str],
    ) -> httpx.Response:
        self.requests.append({"url": url, "json": json, "headers": headers})
        if self.responses:
            return self.responses.pop(0)
        return _response(200, json={"id": "email_123"})


def _settings(**overrides: object) -> Settings:
    values = {
        "resend_api_key": "re_test_key",
        "notification_from_email": "Leads <notifications@example.com>",
    }
    values.update(overrides)
    return Settings(**values)


@pytest.mark.asyncio
async def test_resend_provider_sends_email_via_https_api() -> None:
    client = MockResendHttpClient()
    provider = ResendEmailProvider(_settings(), http_client=client)
    message = EmailMessage(
        to="owner@example.com",
        subject="New qualified lead: Jane Doe",
        body="Summary: Jane needs roof repair.\nLead score: 100",
    )

    await provider.send_email(message)

    assert len(client.requests) == 1
    request = client.requests[0]
    assert request["url"] == RESEND_API_URL
    assert request["headers"]["Authorization"] == "Bearer re_test_key"
    assert request["json"]["from"] == "Leads <notifications@example.com>"
    assert request["json"]["to"] == ["owner@example.com"]
    assert request["json"]["subject"] == message.subject
    assert request["json"]["text"] == message.body


@pytest.mark.asyncio
async def test_resend_provider_requires_api_key() -> None:
    provider = ResendEmailProvider(
        _settings(resend_api_key=""),
        http_client=MockResendHttpClient(),
    )

    with pytest.raises(ValueError, match="RESEND_API_KEY"):
        await provider.send_email(
            EmailMessage(to="owner@example.com", subject="Test", body="Body"),
        )


@pytest.mark.asyncio
async def test_resend_provider_requires_from_email() -> None:
    provider = ResendEmailProvider(
        _settings(notification_from_email=""),
        http_client=MockResendHttpClient(),
    )

    with pytest.raises(ValueError, match="NOTIFICATION_FROM_EMAIL"):
        await provider.send_email(
            EmailMessage(to="owner@example.com", subject="Test", body="Body"),
        )


@pytest.mark.asyncio
async def test_resend_provider_raises_on_api_error() -> None:
    client = MockResendHttpClient(
        responses=[_response(401, json={"message": "Invalid API key"})],
    )
    provider = ResendEmailProvider(_settings(), http_client=client)

    with pytest.raises(httpx.HTTPStatusError):
        await provider.send_email(
            EmailMessage(to="owner@example.com", subject="Test", body="Body"),
        )


def test_factory_selects_resend_provider() -> None:
    from app.services.notifications.factory import build_email_provider

    provider = build_email_provider(
        Settings(
            notification_provider="resend",
            resend_api_key="re_test_key",
            notification_from_email="notifications@example.com",
        ),
    )

    assert isinstance(provider, ResendEmailProvider)
