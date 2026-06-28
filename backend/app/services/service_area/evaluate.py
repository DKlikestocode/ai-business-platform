from app.agents.lead_agent.models import LeadExtractedData
from app.db.models.company import Company
from app.services.service_area.distance import haversine_km
from app.services.service_area.models import ServiceAreaEvaluation, ServiceAreaStatus
from app.services.service_area.plz import (
    extract_postal_code_from_text,
    lookup_postal_code,
    normalize_postal_code,
)


def resolve_lead_postal_code(data: LeadExtractedData) -> str | None:
    return normalize_postal_code(data.postal_code) or extract_postal_code_from_text(
        data.location,
    )


def evaluate_service_area(
    company: Company | None,
    data: LeadExtractedData,
) -> ServiceAreaEvaluation:
    if company is None:
        return ServiceAreaEvaluation(status=ServiceAreaStatus.NOT_CONFIGURED)

    radius = company.service_radius_km
    if (
        company.service_area_latitude is None
        or company.service_area_longitude is None
        or radius is None
        or radius <= 0
    ):
        return ServiceAreaEvaluation(status=ServiceAreaStatus.NOT_CONFIGURED)

    postal_code = resolve_lead_postal_code(data)
    if postal_code is None:
        return ServiceAreaEvaluation(status=ServiceAreaStatus.UNKNOWN)

    lead_coords = lookup_postal_code(postal_code)
    if lead_coords is None:
        return ServiceAreaEvaluation(
            status=ServiceAreaStatus.UNKNOWN,
            postal_code=postal_code,
        )

    distance_km = haversine_km(
        company.service_area_latitude,
        company.service_area_longitude,
        lead_coords.latitude,
        lead_coords.longitude,
    )
    if distance_km <= radius:
        return ServiceAreaEvaluation(
            status=ServiceAreaStatus.IN_RANGE,
            distance_km=distance_km,
            postal_code=postal_code,
        )

    return ServiceAreaEvaluation(
        status=ServiceAreaStatus.OUT_OF_RANGE,
        distance_km=distance_km,
        postal_code=postal_code,
    )


MISSING_POSTAL_CODE_REPLY_NOTE = (
    "Ohne Ihre Postleitzahl können wir leider nicht einschätzen, "
    "ob Sie in unserem Einsatzgebiet liegen. Bitte nennen Sie Ihre 5-stellige PLZ."
)


def append_missing_postal_code_reply_note(reply: str) -> str:
    if MISSING_POSTAL_CODE_REPLY_NOTE in reply:
        return reply
    return f"{reply.rstrip()}\n\n{MISSING_POSTAL_CODE_REPLY_NOTE}"


def append_service_area_reply_note(
    reply: str,
    evaluation: ServiceAreaEvaluation,
    *,
    radius_km: int | None,
) -> str:
    if evaluation.status == ServiceAreaStatus.IN_RANGE and evaluation.distance_km is not None:
        note = (
            f"Ihre Postleitzahl liegt in unserem Einsatzgebiet "
            f"(ca. {evaluation.distance_km:.0f} km Entfernung)."
        )
    elif evaluation.status == ServiceAreaStatus.OUT_OF_RANGE and evaluation.distance_km is not None:
        radius_label = f"{radius_km} km" if radius_km else "unserem Einsatzgebiet"
        note = (
            f"Ihre Postleitzahl liegt vermutlich außerhalb unseres üblichen Einsatzgebiets "
            f"(ca. {evaluation.distance_km:.0f} km, Grenze {radius_label}). "
            "Wir prüfen, ob wir Ihnen trotzdem helfen können."
        )
    else:
        return reply

    if note in reply:
        return reply
    return f"{reply.rstrip()}\n\n{note}"
