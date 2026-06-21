from app.agents.lead_agent.company_context import build_service_area_prompt
from app.db.models.company import Company


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
    assert "30 km" in prompt


def test_build_service_area_prompt_returns_none_when_unconfigured() -> None:
    company = Company(
        name="Test",
        slug="test",
        email="test@example.com",
    )

    assert build_service_area_prompt(company) is None
