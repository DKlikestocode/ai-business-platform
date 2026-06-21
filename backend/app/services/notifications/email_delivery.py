from dataclasses import dataclass

from app.config import Settings


@dataclass(frozen=True)
class EmailDeliveryStatus:
    provider: str
    ready: bool
    sends_real_email: bool

    def as_dict(self) -> dict[str, str | bool]:
        return {
            "email_delivery_provider": self.provider,
            "email_delivery_ready": self.ready,
            "email_delivery_sends_real_email": self.sends_real_email,
        }


def get_email_delivery_status(settings: Settings) -> EmailDeliveryStatus:
    provider = settings.notification_provider.strip().lower()

    if provider == "logging":
        return EmailDeliveryStatus(
            provider="logging",
            ready=settings.is_development,
            sends_real_email=False,
        )

    if provider == "resend":
        configured = bool(
            settings.resend_api_key.strip() and settings.notification_from_email.strip()
        )
        return EmailDeliveryStatus(
            provider="resend",
            ready=configured,
            sends_real_email=configured,
        )

    if provider == "smtp":
        return EmailDeliveryStatus(
            provider="smtp",
            ready=False,
            sends_real_email=False,
        )

    return EmailDeliveryStatus(
        provider=provider,
        ready=False,
        sends_real_email=False,
    )
