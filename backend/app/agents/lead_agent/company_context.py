"""Build company-specific context for lead capture prompts."""

from app.db.models.company import Company
from app.services.service_area.models import ServiceAreaEvaluation, ServiceAreaStatus


def build_service_area_prompt(company: Company) -> str | None:
    center = (company.service_area_center or "").strip()
    radius = company.service_radius_km

    if not center and radius is None:
        return None

    plz_instruction = (
        "Fragen Sie für die Standortprüfung gezielt nach der 5-stelligen Postleitzahl (PLZ). "
        "Ergänzen Sie optional den Ort oder Stadtteil im Feld location."
    )

    if center and radius is not None and radius > 0:
        return (
            f"Einsatzgebiet des Betriebs: {center} und Umgebung (ca. {radius} km). "
            f"{plz_instruction} "
            "Wenn die PLZ-Prüfung außerhalb des Gebiets liegt, weisen Sie freundlich darauf hin. "
            "Erfinden Sie keine feste Zusage für entfernte Orte."
        )

    if center:
        return (
            f"Einsatzgebiet des Betriebs: {center}. "
            f"{plz_instruction} "
            "Prüfen Sie anhand der PLZ, ob der Betrieb dort tätig ist."
        )

    return (
        f"Der Betrieb nimmt Anfragen bis etwa {radius} km um den Standort an. "
        f"{plz_instruction}"
    )


def build_service_area_status_prompt(evaluation: ServiceAreaEvaluation) -> str | None:
    if evaluation.status == ServiceAreaStatus.UNKNOWN:
        return (
            "Standortprüfung: Ohne gültige Postleitzahl ist keine Einschätzung zum "
            "Einsatzgebiet möglich. Fragen Sie nach der 5-stelligen deutschen PLZ."
        )

    if evaluation.status == ServiceAreaStatus.NOT_CONFIGURED:
        return None

    if evaluation.status == ServiceAreaStatus.IN_RANGE and evaluation.distance_km is not None:
        return (
            f"Standortprüfung (verbindlich): PLZ {evaluation.postal_code} liegt im Einsatzgebiet "
            f"(ca. {evaluation.distance_km:.0f} km). Bestätigen Sie das kurz, wenn passend."
        )

    if evaluation.status == ServiceAreaStatus.OUT_OF_RANGE and evaluation.distance_km is not None:
        return (
            f"Standortprüfung (verbindlich): PLZ {evaluation.postal_code} liegt vermutlich "
            f"außerhalb des Einsatzgebiets (ca. {evaluation.distance_km:.0f} km). "
            "Weisen Sie freundlich darauf hin und nehmen Sie die Anfrage trotzdem auf."
        )

    return None
