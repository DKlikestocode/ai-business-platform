"""Channel-neutral intake processing."""

from app.services.intake.models import (
    IntakeChannel,
    IntakeExtraction,
    IntakeScope,
    IntakeStatus,
    ParsedAttachment,
    ParsedEmail,
)

__all__ = [
    "IntakeChannel",
    "IntakeExtraction",
    "IntakeScope",
    "IntakeStatus",
    "ParsedAttachment",
    "ParsedEmail",
]
