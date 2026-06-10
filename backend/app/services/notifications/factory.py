from app.config import Settings
from app.services.notifications.interface import EmailProvider
from app.services.notifications.logging_provider import LoggingEmailProvider
from app.services.notifications.resend_provider import ResendEmailProvider
from app.services.notifications.smtp_provider import SmtpEmailProvider


def build_email_provider(settings: Settings) -> EmailProvider:
    provider = settings.notification_provider.lower()
    if provider == "logging":
        return LoggingEmailProvider()
    if provider == "smtp":
        return SmtpEmailProvider(settings)
    if provider == "resend":
        return ResendEmailProvider(settings)
    raise ValueError(f"Unsupported notification provider: {settings.notification_provider}")
