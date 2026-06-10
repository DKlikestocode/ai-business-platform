from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    body: str
    html: str | None = None


@runtime_checkable
class EmailProvider(Protocol):
    """Contract for outbound email delivery providers."""

    async def send_email(self, message: EmailMessage) -> None:
        """Deliver an email message."""
