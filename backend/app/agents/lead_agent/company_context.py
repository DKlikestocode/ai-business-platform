"""Build company-specific context for lead capture prompts."""

from app.db.models.company import Company
from app.services.service_area.models import ServiceAreaEvaluation, ServiceAreaStatus


def build_service_area_prompt(company: Company) -> str | None:
    center = (company.service_area_center or "").strip()
    radius = company.service_radius_km

    if not center and radius is None:
        return None

    plz_instruction = (
        "Fragen Sie für die Standortprüfung nach der 5-stelligen Postleitzahl (PLZ) — "
        "am besten eingebettet, nachdem Sie das Anliegen kurz verstanden haben. "
        "Ergänzen Sie optional den Ort oder Stadtteil im Feld location."
    )

    no_distance_instruction = (
        "Nennen Sie dem Kunden keine Kilometer-Entfernungen, Radius- oder Distanzangaben."
    )

    if center and radius is not None and radius > 0:
        return (
            f"Einsatzgebiet des Betriebs: {center} und Umgebung. "
            f"{plz_instruction} "
            "Wenn die PLZ-Prüfung außerhalb des Gebiets liegt, weisen Sie freundlich darauf hin. "
            "Erfinden Sie keine feste Zusage für entfernte Orte. "
            f"{no_distance_instruction}"
        )

    if center:
        return (
            f"Einsatzgebiet des Betriebs: {center}. "
            f"{plz_instruction} "
            "Prüfen Sie anhand der PLZ, ob der Betrieb dort tätig ist. "
            f"{no_distance_instruction}"
        )

    return (
        "Der Betrieb hat ein begrenztes Einsatzgebiet um den Standort. "
        f"{plz_instruction} {no_distance_instruction}"
    )


def build_service_area_status_prompt(evaluation: ServiceAreaEvaluation) -> str | None:
    if evaluation.status == ServiceAreaStatus.UNKNOWN:
        return (
            "Standortprüfung: Ohne gültige Postleitzahl ist keine Einschätzung zum "
            "Einsatzgebiet möglich. Fragen Sie nach der 5-stelligen deutschen PLZ."
        )

    if evaluation.status == ServiceAreaStatus.NOT_CONFIGURED:
        return None

    if evaluation.status == ServiceAreaStatus.IN_RANGE:
        return (
            f"Standortprüfung (intern): PLZ {evaluation.postal_code} liegt im Einsatzgebiet. "
            "Bauen Sie das natürlich in Ihre Antwort ein — keine separate Wiederholung oder Zusatzzeile."
        )

    if evaluation.status == ServiceAreaStatus.OUT_OF_RANGE:
        return (
            f"Standortprüfung (intern): PLZ {evaluation.postal_code} liegt vermutlich "
            "außerhalb des Einsatzgebiets. Weisen Sie freundlich darauf hin und nehmen Sie die "
            "Anfrage trotzdem auf — ohne Kilometer-Angaben und ohne separate Zusatzzeile."
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
