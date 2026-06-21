import pytest

from app.agents.lead_agent.contact_validation import (
    RejectedContactFields,
    build_invalid_contact_reply,
    is_valid_email,
    is_valid_phone,
    sanitize_contact_fields,
)
from app.agents.lead_agent.models import LeadExtractedData


@pytest.mark.parametrize(
    "phone",
    [
        "01701234567",
        "+49 170 1234567",
        "030 12345678",
        "0049 30 12345678",
    ],
)
def test_is_valid_phone_accepts_realistic_german_numbers(phone: str) -> None:
    assert is_valid_phone(phone) is True


@pytest.mark.parametrize(
    "phone",
    [
        "123",
        "abc",
        "555-0100",
        "00000000",
        "",
    ],
)
def test_is_valid_phone_rejects_invalid_numbers(phone: str) -> None:
    assert is_valid_phone(phone) is False


@pytest.mark.parametrize(
    "email",
    [
        "kontakt@beispiel.de",
        "max.mueller+anfrage@firma.com",
    ],
)
def test_is_valid_email_accepts_realistic_addresses(email: str) -> None:
    assert is_valid_email(email) is True


@pytest.mark.parametrize(
    "email",
    [
        "keine-email",
        "foo@",
        "@bar.de",
        "foo@bar",
    ],
)
def test_is_valid_email_rejects_invalid_addresses(email: str) -> None:
    assert is_valid_email(email) is False


def test_sanitize_contact_fields_rejects_invalid_phone() -> None:
    data = LeadExtractedData(phone="123", name="Max")

    cleaned, rejected = sanitize_contact_fields(data)

    assert cleaned.phone is None
    assert cleaned.name == "Max"
    assert rejected.phone is True
    assert rejected.email is False


def test_build_invalid_contact_reply_for_phone() -> None:
    reply = build_invalid_contact_reply(RejectedContactFields(phone=True))

    assert "Telefonnummer" in reply
    assert "0170" in reply
