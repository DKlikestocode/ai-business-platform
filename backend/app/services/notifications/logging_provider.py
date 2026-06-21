import logging

from app.services.notifications.interface import EmailMessage

logger = logging.getLogger(__name__)


class LoggingEmailProvider:
    """Development provider that writes email payloads to application logs."""

    async def send_email(self, message: EmailMessage) -> None:
        if "Passwort zurücksetzen" in message.subject:
            reset_url = next(
                (line.strip() for line in message.body.splitlines() if line.startswith("http")),
                message.body,
            )
            logger.info(
                "PASSWORD_RESET_EMAIL to=%s reset_url=%s",
                message.to,
                reset_url,
            )
            return

        logger.info(
            "LEAD_NOTIFICATION_EMAIL to=%s subject=%s body=%s",
            message.to,
            message.subject,
            message.body,
        )
