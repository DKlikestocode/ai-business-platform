from app.agents.lead_agent.models import LeadExtractedData
from app.db.models.company import Company
from app.services.service_area.distance import haversine_km
from app.services.service_area.evaluate import (
    evaluate_service_area,
    is_service_area_configured,
    resolve_lead_postal_code,
)
from app.services.service_area.models import ServiceAreaEvaluation, ServiceAreaStatus
from app.services.service_area.plz import (
    extract_postal_code_from_text,
    lookup_postal_code,
    normalize_postal_code,
)


def test_normalize_postal_code_accepts_five_digits() -> None:
    assert normalize_postal_code(" 80331 ") == "80331"


def test_extract_postal_code_from_text() -> None:
    assert extract_postal_code_from_text("Berlin 10115") == "10115"


def test_lookup_postal_code_returns_coordinates() -> None:
    coords = lookup_postal_code("80331")
    assert coords is not None
    assert 47 < coords.latitude < 49
    assert 10 < coords.longitude < 12


def test_haversine_km_munich_to_nearby() -> None:
    munich = lookup_postal_code("80331")
    starnberg = lookup_postal_code("82319")
    assert munich is not None and starnberg is not None
    distance = haversine_km(
        munich.latitude,
        munich.longitude,
        starnberg.latitude,
        starnberg.longitude,
    )
    assert 20 < distance < 40


def test_evaluate_service_area_in_range() -> None:
    center = lookup_postal_code("80331")
    assert center is not None
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
        service_area_latitude=center.latitude,
        service_area_longitude=center.longitude,
        service_radius_km=30,
    )
    data = LeadExtractedData(postal_code="80331", location="München")

    result = evaluate_service_area(company, data)

    assert result.status == ServiceAreaStatus.IN_RANGE
    assert result.distance_km is not None
    assert result.distance_km < 1


def test_evaluate_service_area_out_of_range() -> None:
    center = lookup_postal_code("80331")
    assert center is not None
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
        service_area_latitude=center.latitude,
        service_area_longitude=center.longitude,
        service_radius_km=25,
    )
    data = LeadExtractedData(postal_code="10115", location="Berlin")

    result = evaluate_service_area(company, data)

    assert result.status == ServiceAreaStatus.OUT_OF_RANGE
    assert result.distance_km is not None
    assert result.distance_km > 400


def test_evaluate_service_area_unknown_without_plz() -> None:
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
        service_area_latitude=48.137,
        service_area_longitude=11.576,
        service_radius_km=30,
    )
    data = LeadExtractedData(location="bei mir")

    result = evaluate_service_area(company, data)

    assert result.status == ServiceAreaStatus.UNKNOWN


def test_is_service_area_configured_requires_coordinates_and_radius() -> None:
    company = Company(
        name="Acme",
        slug="acme",
        email="a@acme.co",
        service_area_center="München",
        service_radius_km=25,
        service_area_latitude=48.137,
        service_area_longitude=11.575,
    )
    assert is_service_area_configured(company) is True

    incomplete = Company(
        name="Acme",
        slug="acme-2",
        email="a@acme.co",
        service_area_center="München",
        service_radius_km=25,
    )
    assert is_service_area_configured(incomplete) is False



def test_resolve_lead_postal_code_prefers_field() -> None:
    data = LeadExtractedData(postal_code="80331", location="Berlin 10115")
    assert resolve_lead_postal_code(data) == "80331"
