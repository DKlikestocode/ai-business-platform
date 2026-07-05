from app.config import Settings
from app.services.notifications.sms_interface import SmsProvider
from app.services.notifications.sms_logging_provider import LoggingSmsProvider


def build_sms_provider(settings: Settings) -> SmsProvider:
    provider = settings.sms_provider.lower()
    if provider == "logging":
        return LoggingSmsProvider()
    raise ValueError(f"Unsupported SMS provider: {settings.sms_provider}")
