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
        service_area_latitude=52.52,
        service_area_longitude=13.405,
    )

    prompt = build_service_area_prompt(company)

    assert prompt is not None
    assert "Berlin" in prompt
    assert "Umgebung" in prompt
    assert "Postleitzahl" in prompt
    assert "keine Kilometer-Entfernungen" in prompt
    assert "nicht erwähnen, dass der Ort im Einsatzgebiet ist" in prompt
    assert "außerhalb des Einsatzgebiets" in prompt


def test_build_service_area_prompt_center_only_no_radius_feedback() -> None:
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
        service_area_center="Berlin",
    )

    prompt = build_service_area_prompt(company)

    assert prompt is not None
    assert "Ohne eingestellten Umkreis-Radius" in prompt
    assert "außerhalb des Einsatzgebiets" not in prompt


def test_build_service_area_prompt_returns_none_when_unconfigured() -> None:
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
    )

    assert build_service_area_prompt(company) is None


def test_build_service_area_status_prompt_in_range_is_silent() -> None:
    prompt = build_service_area_status_prompt(
        ServiceAreaEvaluation(
            status=ServiceAreaStatus.IN_RANGE,
            postal_code="22303",
            distance_km=12.4,
        ),
    )

    assert prompt is None


def test_build_service_area_status_prompt_out_of_range_when_radius_configured() -> None:
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
        service_area_center="Hamburg",
        service_radius_km=25,
        service_area_latitude=53.55,
        service_area_longitude=9.99,
    )
    prompt = build_service_area_status_prompt(
        ServiceAreaEvaluation(
            status=ServiceAreaStatus.OUT_OF_RANGE,
            postal_code="80331",
            distance_km=612.0,
        ),
        company=company,
    )

    assert prompt is not None
    assert "außerhalb des Einsatzgebiets" in prompt
    assert "km" not in prompt.lower()


def test_build_service_area_status_prompt_out_of_range_skipped_without_radius() -> None:
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
        service_area_center="Hamburg",
    )
    prompt = build_service_area_status_prompt(
        ServiceAreaEvaluation(
            status=ServiceAreaStatus.OUT_OF_RANGE,
            postal_code="80331",
        ),
        company=company,
    )

    assert prompt is None


def test_build_service_area_status_prompt_unknown_explains_missing_plz() -> None:
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
        service_area_center="Hamburg",
        service_radius_km=25,
        service_area_latitude=53.55,
        service_area_longitude=9.99,
    )
    prompt = build_service_area_status_prompt(
        ServiceAreaEvaluation(status=ServiceAreaStatus.UNKNOWN),
        company=company,
    )

    assert prompt is not None
    assert "keine Einschätzung" in prompt
    assert "5-stelligen deutschen PLZ" in prompt
