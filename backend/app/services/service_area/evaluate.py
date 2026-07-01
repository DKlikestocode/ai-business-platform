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


def is_service_area_configured(company: Company | None) -> bool:
    if company is None:
        return False

    radius = company.service_radius_km
    return (
        company.service_area_latitude is not None
        and company.service_area_longitude is not None
        and radius is not None
        and radius > 0
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

