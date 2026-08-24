import binascii
import json
from collections.abc import Mapping
from email.utils import parseaddr
from typing import Any
from urllib.parse import urlparse

import httpx
from svix.webhooks import Webhook, WebhookVerificationError

from app.services.intake.email_parser import MAX_EMAIL_BYTES


class ResendWebhookVerificationError(ValueError):
    """Raised when an inbound Resend webhook signature is invalid."""


class ResendFetchError(RuntimeError):
    """Raised when the original received message cannot be retrieved."""


class ResendWebhookVerifier:
    def __init__(self, secret: str) -> None:
        self._webhook = Webhook(secret)

    def verify(self, payload: bytes, headers: Mapping[str, str]) -> dict[str, Any]:
        try:
            self._webhook.verify(payload, headers)
        except (WebhookVerificationError, ValueError, binascii.Error) as exc:
            raise ResendWebhookVerificationError(
                "Invalid Resend webhook signature."
            ) from exc

        try:
            event = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
            raise ResendWebhookVerificationError(
                "Invalid Resend webhook payload."
            ) from exc
        if not isinstance(event, dict):
            raise ResendWebhookVerificationError("Invalid Resend webhook payload.")
        return event


class ResendReceivedEmailClient:
    def __init__(
        self,
        *,
        api_key: str,
        timeout: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._timeout = timeout
        self._client = client

    async def retrieve_raw_message(self, email_id: str) -> bytes:
        client = self._client or httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,
        )
        should_close = self._client is None
        try:
            metadata_response = await client.get(
                f"https://api.resend.com/emails/receiving/{email_id}",
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            metadata_response.raise_for_status()
            metadata = metadata_response.json()
            raw = metadata.get("raw") if isinstance(metadata, dict) else None
            download_url = raw.get("download_url") if isinstance(raw, dict) else None
            if not isinstance(download_url, str) or not download_url:
                raise ResendFetchError("Resend response did not contain a raw email URL.")
            if urlparse(download_url).scheme != "https":
                raise ResendFetchError("Resend raw email URL must use HTTPS.")

            async with client.stream("GET", download_url) as raw_response:
                raw_response.raise_for_status()
                content_length = raw_response.headers.get("content-length")
                if content_length and int(content_length) > MAX_EMAIL_BYTES:
                    raise ResendFetchError("Received email exceeds the 25 MB limit.")
                content = bytearray()
                async for chunk in raw_response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > MAX_EMAIL_BYTES:
                        raise ResendFetchError(
                            "Received email exceeds the 25 MB limit."
                        )
            if not content:
                raise ResendFetchError("Resend returned an empty raw email.")
            return bytes(content)
        except (httpx.HTTPError, ValueError) as exc:
            raise ResendFetchError("Unable to retrieve the received email.") from exc
        finally:
            if should_close:
                await client.aclose()


def extract_received_email_id(event: Mapping[str, Any]) -> str | None:
    if event.get("type") != "email.received":
        return None
    data = event.get("data")
    if not isinstance(data, Mapping):
        return None
    value = data.get("email_id") or data.get("id")
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value[:255] or None


def resolve_company_slug(
    event: Mapping[str, Any],
    *,
    inbound_domain: str,
) -> str | None:
    data = event.get("data")
    if not isinstance(data, Mapping):
        return None
    recipients = data.get("received_for") or data.get("to")
    if isinstance(recipients, str):
        values = [recipients]
    elif isinstance(recipients, list):
        values = [value for value in recipients if isinstance(value, str)]
    else:
        return None

    expected_domain = inbound_domain.strip().lower().rstrip(".")
    for value in values:
        _, address = parseaddr(value)
        local_part, separator, domain = address.lower().rpartition("@")
        if separator and domain.rstrip(".") == expected_domain and local_part:
            return local_part[:255]
    return None
