from app.config import Settings
from app.services.notifications.interface import EmailMessage


class SmtpEmailProvider:
    """SMTP email provider placeholder for future production configuration."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send_email(self, message: EmailMessage) -> None:
        raise NotImplementedError(
            "SMTP email delivery is not configured yet. "
            "Set NOTIFICATION_PROVIDER=logging for development or implement SMTP settings."
        )
