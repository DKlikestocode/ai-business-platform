from datetime import UTC, datetime

import httpx
import pytest
from app.services.intake.resend import (
    ResendFetchError,
    ResendReceivedEmailClient,
    ResendWebhookVerificationError,
    ResendWebhookVerifier,
    extract_received_email_id,
    resolve_company_slug,
)
from svix.webhooks import Webhook


def _event() -> dict[str, object]:
    return {
        "type": "email.received",
        "data": {
            "email_id": "received-email-1",
            "to": ["Demo Betrieb <demo-betrieb@eingang.example.de>"],
        },
    }


def test_extracts_email_id_and_tenant_slug() -> None:
    event = _event()

    assert extract_received_email_id(event) == "received-email-1"
    assert (
        resolve_company_slug(event, inbound_domain="eingang.example.de")
        == "demo-betrieb"
    )
    assert resolve_company_slug(event, inbound_domain="other.example.de") is None


def test_verifies_svix_signature() -> None:
    secret = "whsec_dGVzdC13ZWJob29rLXNlY3JldA=="
    payload = b'{"type":"email.received","data":{"email_id":"email-1"}}'
    timestamp = datetime.now(UTC)
    signature = Webhook(secret).sign("msg_123", timestamp, payload.decode())
    verifier = ResendWebhookVerifier(secret)

    event = verifier.verify(
        payload,
        {
            "svix-id": "msg_123",
            "svix-timestamp": str(int(timestamp.timestamp())),
            "svix-signature": signature,
        },
    )

    assert event["type"] == "email.received"


def test_rejects_invalid_svix_signature() -> None:
    verifier = ResendWebhookVerifier("whsec_dGVzdC13ZWJob29rLXNlY3JldA==")

    with pytest.raises(ResendWebhookVerificationError):
        verifier.verify(
            b"{}",
            {
                "svix-id": "msg_123",
                "svix-timestamp": str(int(datetime.now(UTC).timestamp())),
                "svix-signature": "v1,invalid",
            },
        )


@pytest.mark.asyncio
async def test_retrieves_raw_message_without_forwarding_api_key() -> None:
    raw_message = b"From: customer@example.com\r\nSubject: Test\r\n\r\nBody"
    seen_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        if request.url.host == "api.resend.com":
            return httpx.Response(
                200,
                json={
                    "raw": {
                        "download_url": "https://storage.example.test/message.eml"
                    }
                },
            )
        return httpx.Response(200, content=raw_message)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        follow_redirects=True,
    ) as http_client:
        client = ResendReceivedEmailClient(
            api_key="resend-secret",
            client=http_client,
        )
        result = await client.retrieve_raw_message("received-email-1")

    assert result == raw_message
    assert seen_requests[0].headers["authorization"] == "Bearer resend-secret"
    assert "authorization" not in seen_requests[1].headers


@pytest.mark.asyncio
async def test_rejects_insecure_raw_download_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"raw": {"download_url": "http://storage.example.test/message.eml"}},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = ResendReceivedEmailClient(api_key="secret", client=http_client)
        with pytest.raises(ResendFetchError):
            await client.retrieve_raw_message("received-email-1")
