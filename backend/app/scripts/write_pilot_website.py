"""Write a minimal pilot marketing page with the tokenized widget embed."""

from __future__ import annotations

import argparse
import sys

from app.config import get_settings
from app.db.models.company import Company
from app.db.session import SessionLocal
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.services.activation.embed import build_widget_embed_snippet


def build_pilot_website_html(*, company_slug: str, install_token: str, api_base: str) -> str:
    snippet = build_widget_embed_snippet(
        company_slug=company_slug,
        install_token=install_token,
        api_base=api_base,
    ).replace("/static/widget/widget.js", "/static/widget/widget.js?v=3")

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Willkommen</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      max-width: 40rem;
      margin: 3rem auto;
      padding: 0 1rem;
      line-height: 1.5;
    }}
    h1 {{ font-size: 1.75rem; }}
    p {{ color: #374151; }}
  </style>
</head>
<body>
  <h1>Willkommen</h1>
  <p>Schreiben Sie uns im Chat unten rechts — wir melden uns schnellstmöglich.</p>
  {snippet}
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print HTML for the pilot marketing site with widget embed.",
    )
    parser.add_argument(
        "--company-slug",
        default=None,
        help="Company slug (defaults to the oldest company).",
    )
    args = parser.parse_args()

    settings = get_settings()
    api_base = settings.public_api_base_url or "https://api.example.com"

    with SessionLocal() as session:
        company_repo = CompanyRepository(session)
        if args.company_slug:
            company = company_repo.get_by_slug(args.company_slug)
            if company is None:
                raise SystemExit(f"Company not found for slug: {args.company_slug}")
        else:
            company = session.query(Company).order_by(Company.created_at).first()
            if company is None:
                raise SystemExit("No company found.")

        activation = CompanyActivationRepository(session).get_or_create(company.id)
        html = build_pilot_website_html(
            company_slug=company.slug,
            install_token=activation.install_token,
            api_base=api_base,
        )

    sys.stdout.write(html)


if __name__ == "__main__":
    main()
