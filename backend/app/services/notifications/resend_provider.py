from typing import Any, Protocol, runtime_checkable

import httpx

from app.config import Settings
from app.services.notifications.interface import EmailMessage

RESEND_API_URL = "https://api.resend.com/emails"


@runtime_checkable
class ResendHttpClient(Protocol):
    async def post(
        self,
        url: str,
        *,
        json: dict[str, Any],
        headers: dict[str, str],
    ) -> httpx.Response:
        """POST JSON payload to the Resend API."""


class ResendEmailProvider:
    """Send lead notification emails through the Resend HTTPS API."""

    def __init__(
        self,
        settings: Settings,
        *,
        http_client: ResendHttpClient | None = None,
    ) -> None:
        self._settings = settings
        self._http_client = http_client

    async def send_email(self, message: EmailMessage) -> None:
        api_key = self._settings.resend_api_key.strip()
        from_email = self._settings.notification_from_email.strip()
        if not api_key:
            raise ValueError("RESEND_API_KEY is required when NOTIFICATION_PROVIDER=resend.")
        if not from_email:
            raise ValueError(
                "NOTIFICATION_FROM_EMAIL is required when NOTIFICATION_PROVIDER=resend."
            )

        payload: dict[str, Any] = {
            "from": from_email,
            "to": [message.to],
            "subject": message.subject,
            "text": message.body,
        }
        if message.html:
            payload["html"] = message.html

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        if self._http_client is not None:
            response = await self._http_client.post(
                RESEND_API_URL,
                json=payload,
                headers=headers,
            )
        else:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    RESEND_API_URL,
                    json=payload,
                    headers=headers,
                )

        response.raise_for_status()
