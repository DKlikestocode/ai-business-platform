from app.db.models.company import Company
from app.services.service_area.geocode import resolve_coordinates_from_text


def refresh_company_service_area_coordinates(company: Company) -> None:
    center = (company.service_area_center or "").strip()
    if not center:
        company.service_area_latitude = None
        company.service_area_longitude = None
        return

    coords = resolve_coordinates_from_text(center)
    if coords is None:
        company.service_area_latitude = None
        company.service_area_longitude = None
        return

    company.service_area_latitude = coords.latitude
    company.service_area_longitude = coords.longitude
