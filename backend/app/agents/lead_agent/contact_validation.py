import re
from dataclasses import dataclass

from app.agents.lead_agent.models import LeadExtractedData

_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
_NON_DIGIT_PATTERN = re.compile(r"\D")


@dataclass(frozen=True)
class RejectedContactFields:
    phone: bool = False
    email: bool = False

    @property
    def any_rejected(self) -> bool:
        return self.phone or self.email


def extract_phone_digits(phone: str) -> str:
    digits = _NON_DIGIT_PATTERN.sub("", phone.strip())
    if digits.startswith("00"):
        return digits[2:]
    return digits


def is_valid_phone(phone: str | None) -> bool:
    if phone is None or not str(phone).strip():
        return False

    digits = extract_phone_digits(phone)
    if not digits.isdigit():
        return False
    if len(digits) < 8 or len(digits) > 15:
        return False
    if len(set(digits)) == 1:
        return False
    return True


def is_valid_email(email: str | None) -> bool:
    if email is None or not str(email).strip():
        return False

    normalized = email.strip()
    if len(normalized) > 254:
        return False
    return bool(_EMAIL_PATTERN.match(normalized))


def sanitize_contact_fields(data: LeadExtractedData) -> tuple[LeadExtractedData, RejectedContactFields]:
    rejected = RejectedContactFields()
    cleaned = data.model_copy(deep=True)

    if cleaned.phone is not None and str(cleaned.phone).strip() and not is_valid_phone(cleaned.phone):
        cleaned.phone = None
        rejected = RejectedContactFields(phone=True, email=rejected.email)

    if cleaned.email is not None and str(cleaned.email).strip() and not is_valid_email(cleaned.email):
        cleaned.email = None
        rejected = RejectedContactFields(phone=rejected.phone, email=True)

    return cleaned, rejected


def build_invalid_contact_reply(rejected: RejectedContactFields) -> str:
    if rejected.phone and rejected.email:
        return (
            "Die Telefonnummer und die E-Mail-Adresse konnte ich leider nicht erkennen. "
            "Bitte geben Sie eine gültige Nummer (z. B. 0170 1234567) "
            "oder eine gültige E-Mail-Adresse (z. B. name@beispiel.de) an."
        )
    if rejected.phone:
        return (
            "Die Telefonnummer konnte ich leider nicht erkennen. "
            "Bitte geben Sie eine gültige Nummer an, zum Beispiel 0170 1234567 "
            "oder +49 170 1234567."
        )
    return (
        "Die E-Mail-Adresse scheint ungültig zu sein. "
        "Bitte prüfen Sie die Schreibweise, zum Beispiel name@beispiel.de."
    )
