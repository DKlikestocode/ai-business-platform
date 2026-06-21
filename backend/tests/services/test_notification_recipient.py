from app.services.notifications.recipient import (
    is_notification_configured,
    resolve_notification_recipient,
)


def test_resolve_notification_recipient_prefers_notification_email() -> None:
    from app.db.models.company import Company

    company = Company(
        name="Acme",
        slug="acme",
        email="office@acme.co",
        notification_email="alerts@acme.co",
    )
    assert resolve_notification_recipient(company) == "alerts@acme.co"


def test_resolve_notification_recipient_falls_back_to_company_email() -> None:
    from app.db.models.company import Company

    company = Company(
        name="Acme",
        slug="acme",
        email="office@acme.co",
        notification_email=None,
    )
    assert resolve_notification_recipient(company) == "office@acme.co"
    assert is_notification_configured(company) is True
