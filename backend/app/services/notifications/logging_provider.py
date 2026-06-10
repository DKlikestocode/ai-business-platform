import logging

from app.services.notifications.interface import EmailMessage

logger = logging.getLogger(__name__)


class LoggingEmailProvider:
    """Development provider that writes email payloads to application logs."""

    async def send_email(self, message: EmailMessage) -> None:
        logger.info(
            "LEAD_NOTIFICATION_EMAIL to=%s subject=%s body=%s",
            message.to,
            message.subject,
            message.body,
        )
