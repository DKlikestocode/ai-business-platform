"""Write a pilot marketing page with the tokenized widget embed."""

from __future__ import annotations

import argparse
import sys

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models.company import Company
from app.db.session import SessionLocal
from app.demo.pilot_website_template import PilotWebsiteContent, build_pilot_website_html
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.services.activation.embed import build_widget_embed_snippet

_PILOT_EXCLUDED_SLUGS = frozenset({"default", "demo-company"})


def resolve_pilot_company(
    session: Session,
    company_repo: CompanyRepository,
    *,
    company_slug: str | None,
) -> Company:
    if company_slug:
        company = company_repo.get_by_slug(company_slug)
        if company is None:
            raise SystemExit(f"Company not found for slug: {company_slug}")
        return company

    companies = session.query(Company).order_by(Company.created_at).all()
    for company in companies:
        if company.slug not in _PILOT_EXCLUDED_SLUGS:
            return company

    if companies:
        return companies[0]

    raise SystemExit("No company found.")


def build_pilot_website_html_for_company(
    *,
    company: Company,
    install_token: str,
    api_base: str,
) -> str:
    snippet = build_widget_embed_snippet(
        company_slug=company.slug,
        install_token=install_token,
        api_base=api_base,
    ).replace("/static/widget/widget.js", "/static/widget/widget.js?v=3")

    return build_pilot_website_html(
        PilotWebsiteContent(
            company_name=company.name,
            trade=company.trade,
            email=company.email,
            phone=company.phone,
            service_area_center=company.service_area_center,
            service_radius_km=company.service_radius_km,
            widget_snippet=snippet,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print HTML for the pilot marketing site with widget embed.",
    )
    parser.add_argument(
        "--company-slug",
        default=None,
        help="Company slug (defaults to the first real pilot company).",
    )
    args = parser.parse_args()

    settings = get_settings()
    api_base = settings.public_api_base_url or "https://api.example.com"

    with SessionLocal() as session:
        company_repo = CompanyRepository(session)
        company = resolve_pilot_company(
            session,
            company_repo,
            company_slug=args.company_slug,
        )
        activation = CompanyActivationRepository(session).get_or_create(company.id)
        html = build_pilot_website_html_for_company(
            company=company,
            install_token=activation.install_token,
            api_base=api_base,
        )

    sys.stdout.write(html)


if __name__ == "__main__":
    main()
