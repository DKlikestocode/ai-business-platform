from app.agents.lead_agent.company_context import (
    build_service_area_prompt,
    build_service_area_status_prompt,
)
from app.db.models.company import Company
from app.services.service_area.models import ServiceAreaEvaluation, ServiceAreaStatus


def test_build_service_area_prompt_with_center_and_radius() -> None:
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
        service_area_center="Berlin",
        service_radius_km=30,
    )

    prompt = build_service_area_prompt(company)

    assert prompt is not None
    assert "Berlin" in prompt
    assert "Umgebung" in prompt
    assert "Postleitzahl" in prompt
    assert "keine Kilometer-Entfernungen" in prompt


def test_build_service_area_prompt_returns_none_when_unconfigured() -> None:
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
    )

    assert build_service_area_prompt(company) is None


def test_build_service_area_status_prompt_in_range_without_distance() -> None:
    prompt = build_service_area_status_prompt(
        ServiceAreaEvaluation(
            status=ServiceAreaStatus.IN_RANGE,
            postal_code="22303",
            distance_km=12.4,
        ),
    )

    assert prompt is not None
    assert "im Einsatzgebiet" in prompt
    assert "km" not in prompt.lower()


def test_build_service_area_status_prompt_unknown_explains_missing_plz() -> None:
    prompt = build_service_area_status_prompt(
        ServiceAreaEvaluation(status=ServiceAreaStatus.UNKNOWN),
    )

    assert prompt is not None
    assert "keine Einschätzung" in prompt
    assert "5-stelligen deutschen PLZ" in prompt
