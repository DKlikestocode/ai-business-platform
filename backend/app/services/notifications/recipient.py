from app.db.models.company import Company


def resolve_notification_recipient(company: Company) -> str | None:
    explicit = (company.notification_email or "").strip()
    if explicit:
        return explicit
    fallback = (company.email or "").strip()
    return fallback or None


def is_notification_configured(company: Company) -> bool:
    return resolve_notification_recipient(company) is not None
