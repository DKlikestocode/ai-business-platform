"""Build company-specific context for lead capture prompts."""

from app.db.models.company import Company


def build_service_area_prompt(company: Company) -> str | None:
    center = (company.service_area_center or "").strip()
    radius = company.service_radius_km

    if not center and radius is None:
        return None

    if center and radius is not None and radius > 0:
        return (
            f"Einsatzgebiet des Betriebs: {center} und Umgebung (ca. {radius} km). "
            "Fragen Sie bei Anfragen außerhalb dieses Gebiets freundlich nach dem "
            "Standort und weisen Sie darauf hin, wenn der Ort vermutlich außerhalb "
            "des Einsatzgebiets liegt. Erfinden Sie keine feste Zusage für entfernte Orte."
        )

    if center:
        return (
            f"Einsatzgebiet des Betriebs: {center}. "
            "Fragen Sie bei Anfragen aus anderen Regionen nach dem Standort und "
            "prüfen Sie, ob der Betrieb dort tätig ist."
        )

    return (
        f"Der Betrieb nimmt Anfragen bis etwa {radius} km um den Standort an. "
        "Fragen Sie bei unklarem Standort nach dem Ort."
    )
