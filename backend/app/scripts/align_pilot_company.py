"""Point a dashboard user at the canonical pilot company slug used by the public business site."""

from __future__ import annotations

import argparse

from sqlalchemy import func, select

from app.db.models.company import Company
from app.db.models.lead import Lead
from app.db.models.user import User
from app.db.session import SessionLocal
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository


def align_pilot_company(
    *,
    user_email: str,
    target_slug: str,
    company_name: str | None = None,
    public_email: str | None = None,
    phone: str | None = None,
    session=None,
) -> str:
    owns_session = session is None
    session = session or SessionLocal()
    try:
        user_repo = UserRepository(session)
        company_repo = CompanyRepository(session)

        user = user_repo.get_by_email(user_email.strip())
        if user is None:
            raise ValueError(f"User with email '{user_email}' not found.")

        company = company_repo.get_by_id(user.company_id)
        if company is None:
            raise ValueError(f"Company for user '{user_email}' not found.")

        duplicate = company_repo.get_by_slug(target_slug)
        if duplicate is not None and duplicate.id != company.id:
            duplicate_users = session.scalar(
                select(func.count()).select_from(User).where(User.company_id == duplicate.id),
            )
            duplicate_leads = session.scalar(
                select(func.count()).select_from(Lead).where(Lead.company_id == duplicate.id),
            )
            if duplicate_users or duplicate_leads:
                raise ValueError(
                    f"Slug '{target_slug}' is already used by another company with data.",
                )
            session.delete(duplicate)
            session.flush()

        if company.slug != target_slug:
            company.slug = target_slug

        updates: dict[str, object] = {}
        if company_name:
            updates["name"] = company_name
        if public_email:
            updates["email"] = public_email
        if phone is not None:
            updates["phone"] = phone or None

        if updates:
            company_repo.update_settings(company, **updates)

        session.commit()
        session.refresh(company)
        return company.slug
    finally:
        if owns_session:
            session.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Align a dashboard user's company with the public business site slug "
            "(PILOT_COMPANY_SLUG / SITE_COMPANY_SLUG)."
        ),
    )
    parser.add_argument("--user-email", required=True)
    parser.add_argument("--target-slug", required=True)
    parser.add_argument("--company-name", default=None)
    parser.add_argument("--public-email", default=None)
    parser.add_argument("--phone", default=None)
    args = parser.parse_args()

    slug = align_pilot_company(
        user_email=args.user_email,
        target_slug=args.target_slug.strip(),
        company_name=args.company_name,
        public_email=args.public_email,
        phone=args.phone,
    )
    print(f"Pilot company slug is now '{slug}' for user {args.user_email}.")


if __name__ == "__main__":
    main()
