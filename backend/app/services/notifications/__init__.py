"""Lead notification services."""

from app.services.notifications.interface import EmailMessage, EmailProvider

__all__ = [
    "EmailMessage",
    "EmailProvider",
]
