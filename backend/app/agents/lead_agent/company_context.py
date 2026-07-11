"""Build company-specific context for lead capture prompts."""

from app.db.models.company import Company
from app.services.service_area.evaluate import is_service_area_configured
from app.services.service_area.models import ServiceAreaEvaluation, ServiceAreaStatus


def build_service_area_prompt(company: Company) -> str | None:
    center = (company.service_area_center or "").strip()
    radius_configured = is_service_area_configured(company)

    if not center and not radius_configured:
        return None

    plz_instruction = (
        "Fragen Sie für die Standortprüfung nach der 5-stelligen Postleitzahl (PLZ) — "
        "am besten eingebettet, nachdem Sie das Anliegen kurz verstanden haben. "
        "Ergänzen Sie optional den Ort oder Stadtteil im Feld location."
    )

    no_distance_instruction = (
        "Nennen Sie dem Kunden keine Kilometer-Entfernungen, Radius- oder Distanzangaben."
    )

    never_confirm_in_range = (
        "Wenn die Postleitzahl im Einsatzgebiet liegt: keine Bestätigung an den Kunden — "
        "nicht erwähnen, dass der Ort im Einsatzgebiet ist. Einfach mit der Anfrage fortfahren."
    )

    if radius_configured:
        return (
            f"Einsatzgebiet des Betriebs: {center or 'konfigurierter Standort'} und Umgebung. "
            f"{plz_instruction} "
            "Liegt die PLZ außerhalb des Einsatzgebiets, weisen Sie freundlich darauf hin "
            "und nehmen Sie die Anfrage trotzdem auf. "
            f"{never_confirm_in_range} "
            f"{no_distance_instruction}"
        )

    if center:
        return (
            f"Standort des Betriebs: {center}. "
            f"{plz_instruction} "
            "Ohne eingestellten Umkreis-Radius keine Einsatzgebiet-Bestätigung oder "
            "-Ablehnung an den Kunden. "
            f"{no_distance_instruction}"
        )

    return None


def build_service_area_status_prompt(
    evaluation: ServiceAreaEvaluation,
    *,
    company: Company | None = None,
) -> str | None:
    if evaluation.status == ServiceAreaStatus.UNKNOWN:
        if company is not None and not is_service_area_configured(company):
            return None
        return (
            "Standortprüfung: Ohne gültige Postleitzahl ist keine Einschätzung zum "
            "Einsatzgebiet möglich. Fragen Sie nach der 5-stelligen deutschen PLZ."
        )

    if evaluation.status == ServiceAreaStatus.NOT_CONFIGURED:
        return None

    if evaluation.status == ServiceAreaStatus.IN_RANGE:
        return None

    if evaluation.status == ServiceAreaStatus.OUT_OF_RANGE:
        if company is not None and not is_service_area_configured(company):
            return None
        return (
            f"Standortprüfung (intern): PLZ {evaluation.postal_code} liegt vermutlich "
            "außerhalb des Einsatzgebiets. Weisen Sie freundlich darauf hin und nehmen Sie die "
            "Anfrage trotzdem auf — ohne Kilometer-Angaben."
        )

    return None


def build_business_contact_prompt(company: Company) -> str | None:
    share_phone = company.chat_share_phone and bool((company.phone or "").strip())
    share_email = company.chat_share_email and bool((company.email or "").strip())

    if not share_phone and not share_email:
        return None

    lines = [
        "Der Betrieb erlaubt, folgende Kontaktdaten im Chat zu nennen, wenn der Kunde "
        "danach fragt oder direkten Kontakt wünscht:",
    ]
    if share_phone:
        lines.append(f"- Telefon: {company.phone}")
    if share_email:
        lines.append(f"- E-Mail: {company.email}")
    lines.append(
        "Nennen Sie diese Angaben nur auf Nachfrage oder am Ende bei der Bestätigung — "
        "nicht zu Beginn des Gesprächs."
    )
    return "\n".join(lines)
