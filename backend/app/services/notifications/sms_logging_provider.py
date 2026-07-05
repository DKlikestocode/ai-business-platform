import logging

from app.services.notifications.sms_interface import SmsMessage, SmsProvider

logger = logging.getLogger(__name__)


class LoggingSmsProvider(SmsProvider):
    async def send_sms(self, message: SmsMessage) -> None:
        logger.info(
            "SMS (logging provider) to=%s body=%s",
            message.to,
            message.body,
        )
