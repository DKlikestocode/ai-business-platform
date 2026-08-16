import hashlib
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path

from app.services.intake.models import ParsedAttachment, ParsedEmail

MAX_EMAIL_BYTES = 25 * 1024 * 1024
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
MAX_ATTACHMENTS = 10


class EmailParseError(ValueError):
    """Raised when an RFC 822 message cannot be safely processed."""


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)


def parse_email(raw_message: bytes) -> ParsedEmail:
    if not raw_message:
        raise EmailParseError("Email message is empty.")
    if len(raw_message) > MAX_EMAIL_BYTES:
        raise EmailParseError("Email message exceeds the 25 MB limit.")

    try:
        message = BytesParser(policy=policy.default).parsebytes(raw_message)
    except Exception as exc:
        raise EmailParseError("Email message is not valid RFC 822 content.") from exc

    if not isinstance(message, EmailMessage):
        raise EmailParseError("Email parser returned an unsupported message type.")

    subject = str(message.get("Subject", "")).strip()
    sender_name, sender_email = parseaddr(str(message.get("From", "")))
    attachments = _parse_attachments(message)

    return ParsedEmail(
        message_id=_clean_message_id(message.get("Message-ID")),
        subject=subject,
        sender_name=sender_name.strip() or None,
        sender_email=sender_email.strip().lower() or None,
        received_at=_parse_date(message.get("Date")),
        body_text=_parse_body(message),
        attachments=attachments,
    )


def source_sha256(raw_message: bytes) -> str:
    return hashlib.sha256(raw_message).hexdigest()


def _parse_attachments(message: EmailMessage) -> list[ParsedAttachment]:
    parsed: list[ParsedAttachment] = []
    for part in message.iter_attachments():
        if len(parsed) >= MAX_ATTACHMENTS:
            raise EmailParseError(
                f"Email contains more than {MAX_ATTACHMENTS} attachments."
            )

        filename = _safe_filename(part.get_filename(), index=len(parsed) + 1)
        content = part.get_payload(decode=True) or b""
        if len(content) > MAX_ATTACHMENT_BYTES:
            raise EmailParseError(f"Attachment '{filename}' exceeds the 10 MB limit.")

        parsed.append(
            ParsedAttachment(
                filename=filename,
                content_type=part.get_content_type(),
                content=content,
                sha256=hashlib.sha256(content).hexdigest(),
            )
        )
    return parsed


def _parse_body(message: EmailMessage) -> str:
    body = message.get_body(preferencelist=("plain", "html"))
    if body is None:
        if message.get_content_maintype() == "text":
            return _part_text(message)
        return ""

    text = _part_text(body)
    if body.get_content_type() != "text/html":
        return text.strip()

    parser = _HTMLTextExtractor()
    parser.feed(text)
    return "\n".join(parser.parts).strip()


def _part_text(part: EmailMessage) -> str:
    try:
        content = part.get_content()
    except (LookupError, UnicodeDecodeError):
        payload = part.get_payload(decode=True) or b""
        return payload.decode("utf-8", errors="replace")
    return content if isinstance(content, str) else ""


def _safe_filename(filename: str | None, *, index: int) -> str:
    cleaned = Path(filename or f"attachment-{index}").name.strip()
    return cleaned[:255] or f"attachment-{index}"


def _clean_message_id(value: str | None) -> str | None:
    cleaned = (value or "").strip()
    return cleaned[:255] or None


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
