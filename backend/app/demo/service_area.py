"""Default service area used when seeding example inquiries."""

from app.db.models.company import Company
from app.repositories.company_repository import CompanyRepository
from app.services.service_area.coordinates import refresh_company_service_area_coordinates

EXAMPLE_SERVICE_AREA_CENTER = "22303 Hamburg"
EXAMPLE_SERVICE_AREA_RADIUS_KM = 40


def ensure_company_service_area_for_examples(
    company_repository: CompanyRepository,
    company: Company,
) -> Company:
    """Ensure coordinates exist so example leads can show service-area badges."""
    center = (company.service_area_center or "").strip()
    radius = company.service_radius_km

    if not center or radius is None or radius <= 0:
        return company_repository.update_settings(
            company,
            service_area_center=EXAMPLE_SERVICE_AREA_CENTER,
            service_radius_km=EXAMPLE_SERVICE_AREA_RADIUS_KM,
        )

    if company.service_area_latitude is None or company.service_area_longitude is None:
        refresh_company_service_area_coordinates(company)
        company_repository._session.commit()
        company_repository._session.refresh(company)

    return company
