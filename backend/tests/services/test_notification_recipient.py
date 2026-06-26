import pytest

from app.db.models.company import Company
from app.services.notifications.recipient import (
    is_notification_configured,
    resolve_notification_recipient,
)


def test_resolve_notification_recipient_prefers_explicit_email() -> None:
    company = Company(
        name="Acme",
        slug="acme",
        email="hello@acme.co",
        notification_email="alerts@acme.co",
    )

    assert resolve_notification_recipient(company) == "alerts@acme.co"
    assert is_notification_configured(company) is True


def test_resolve_notification_recipient_falls_back_to_company_email() -> None:
    company = Company(
        name="Acme",
        slug="acme",
        email="hello@acme.co",
        notification_email=None,
    )

    assert resolve_notification_recipient(company) == "hello@acme.co"
    assert is_notification_configured(company) is True


def test_resolve_notification_recipient_returns_none_when_missing() -> None:
    company = Company(
        name="Acme",
        slug="acme",
        email="",
        notification_email=None,
    )

    assert resolve_notification_recipient(company) is None
    assert is_notification_configured(company) is False
