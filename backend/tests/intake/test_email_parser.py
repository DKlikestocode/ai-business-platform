from email.message import EmailMessage
from pathlib import Path

import pytest
from app.services.intake.email_parser import EmailParseError, parse_email, source_sha256

from .conftest import CASE_DIRECTORIES, load_expected


@pytest.mark.parametrize("case_directory", CASE_DIRECTORIES, ids=lambda path: path.name)
def test_parses_all_synthetic_shk_emails(case_directory: Path) -> None:
    raw_message = (case_directory / "inquiry.eml").read_bytes()
    expected = load_expected(case_directory)

    parsed = parse_email(raw_message)

    assert parsed.subject
    assert parsed.message_id == f"<{case_directory.name}@synthetic-shk.example>"
    expected_sender = (
        "buero@nordbau.example"
        if case_directory.name == "case_007"
        else expected["expected"]["email"]
    )
    assert parsed.sender_email == expected_sender
    assert parsed.body_text.strip()
    assert [attachment.filename for attachment in parsed.attachments] == expected[
        "attachments"
    ]
    assert len(source_sha256(raw_message)) == 64


@pytest.mark.parametrize(
    "case_directory",
    [case for case in CASE_DIRECTORIES if (case / "attachments").is_dir()],
    ids=lambda path: path.name,
)
def test_mime_pdf_bytes_match_reference_files(case_directory: Path) -> None:
    parsed = parse_email((case_directory / "inquiry.eml").read_bytes())

    assert parsed.attachments
    for attachment in parsed.attachments:
        reference = case_directory / "attachments" / attachment.filename
        assert attachment.content_type == "application/pdf"
        assert attachment.is_pdf is True
        assert attachment.content == reference.read_bytes()
        assert attachment.size_bytes == reference.stat().st_size


def test_parses_html_only_email() -> None:
    message = EmailMessage()
    message["From"] = "Maria Beispiel <maria@example.com>"
    message["Subject"] = "Heizung"
    message.set_content("<p>Heizung <strong>ausgefallen</strong>.</p>", subtype="html")

    parsed = parse_email(message.as_bytes())

    assert parsed.body_text == "Heizung\nausgefallen\n."


def test_parses_named_inline_image_from_nested_related_part() -> None:
    message = EmailMessage()
    message["From"] = "Maria Beispiel <maria@example.com>"
    message["Subject"] = "Foto der Heizungsanlage"
    message.set_content("Das Foto ist beigefügt.")
    message.add_alternative(
        '<p>Das Foto ist beigefügt.</p><img src="cid:heating-image">',
        subtype="html",
    )
    html_part = message.get_payload()[1]
    html_part.add_related(
        b"synthetic-png-content",
        maintype="image",
        subtype="png",
        cid="<heating-image>",
        filename="heizungsanlage.png",
        disposition="inline",
    )

    parsed = parse_email(message.as_bytes())

    assert len(parsed.attachments) == 1
    assert parsed.attachments[0].filename == "heizungsanlage.png"
    assert parsed.attachments[0].content_type == "image/png"
    assert parsed.attachments[0].content == b"synthetic-png-content"


def test_rejects_empty_email() -> None:
    with pytest.raises(EmailParseError, match="empty"):
        parse_email(b"")
