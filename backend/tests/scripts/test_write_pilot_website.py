from app.db.models.company import Company
from app.demo.pilot_website_template import PilotWebsiteContent, build_pilot_website_html
from app.scripts.write_pilot_website import (
    build_pilot_website_html_for_company,
    resolve_pilot_company,
)


def test_build_pilot_website_html_includes_widget_embed() -> None:
    html = build_pilot_website_html(
        PilotWebsiteContent(
            company_name="Meister Müller Sanitär",
            trade="skh",
            email="kontakt@beispiel.de",
            phone="+49 40 123456",
            service_area_center="22303 Hamburg",
            service_radius_km=30,
            widget_snippet=(
                '<div id="ai-agent-widget" data-company-slug="acme-plumbing"'
                ' data-install-token="test-install-token"></div>'
                '<script src="https://api.example.com/static/widget/widget.js?v=3"></script>'
            ),
        ),
    )

    assert "Meister Müller Sanitär" in html
    assert "Sanitär · Heizung · Klima" in html
    assert "22303 Hamburg und Umgebung (ca. 30 km)" in html
    assert 'data-company-slug="acme-plumbing"' in html
    assert 'data-install-token="test-install-token"' in html
    assert "https://api.example.com/static/widget/widget.js?v=3" in html
    assert "Unsere Leistungen" in html


def test_build_pilot_website_html_for_company_uses_company_fields() -> None:
    company = Company(
        name="Dominik's Dienstleistungsbetrieb",
        slug="mikes-sanitarbetrieb",
        email="kontakt@beispiel.de",
        phone=None,
        trade="skh",
        service_area_center="22041 Hamburg-Wandsbek",
        service_radius_km=30,
    )

    html = build_pilot_website_html_for_company(
        company=company,
        install_token="token-123",
        api_base="https://api.dominiksdomain.com",
    )

    assert 'data-company-slug="mikes-sanitarbetrieb"' in html
    assert "Dominik&#x27;s Dienstleistungsbetrieb" in html
    assert "22041 Hamburg-Wandsbek und Umgebung" in html


def test_resolve_pilot_company_skips_placeholder_slugs() -> None:
    class FakeQuery:
        def __init__(self, companies: list[Company]) -> None:
            self._companies = companies

        def order_by(self, *_args: object) -> "FakeQuery":
            return self

        def all(self) -> list[Company]:
            return self._companies

    class FakeSession:
        def __init__(self, companies: list[Company]) -> None:
            self._companies = companies

        def query(self, _model: type[Company]) -> FakeQuery:
            return FakeQuery(self._companies)

    companies = [
        Company(name="Default", slug="default", email="a@b.c"),
        Company(name="Demo", slug="demo-company", email="d@e.f"),
        Company(name="Pilot", slug="mikes-sanitarbetrieb", email="p@q.r"),
    ]

    resolved = resolve_pilot_company(
        FakeSession(companies),  # type: ignore[arg-type]
        company_repo=object(),  # type: ignore[arg-type]
        company_slug=None,
    )

    assert resolved.slug == "mikes-sanitarbetrieb"
