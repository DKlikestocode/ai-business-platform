from app.config import Settings
from app.services.notifications.email_delivery import get_email_delivery_status


def test_logging_provider_ready_in_development() -> None:
    status = get_email_delivery_status(
        Settings(app_env="development", notification_provider="logging"),
    )
    assert status.provider == "logging"
    assert status.ready is True
    assert status.sends_real_email is False


def test_resend_provider_requires_keys() -> None:
    missing = get_email_delivery_status(
        Settings(notification_provider="resend", resend_api_key="", notification_from_email=""),
    )
    assert missing.ready is False
    assert missing.sends_real_email is False

    configured = get_email_delivery_status(
        Settings(
            notification_provider="resend",
            resend_api_key="re_test",
            notification_from_email="Agent Platform <noreply@example.com>",
        ),
    )
    assert configured.ready is True
    assert configured.sends_real_email is True
