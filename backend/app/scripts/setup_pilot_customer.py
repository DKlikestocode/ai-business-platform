"""Create a pilot customer company, owner user, and optional notification settings."""

import argparse
import getpass
import secrets
import string

from app.db.session import SessionLocal
from app.demo.pilot_setup import PilotCustomerInput, setup_pilot_customer
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository


def _generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a pilot customer workspace with company and owner user.",
    )
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--company-email", required=True)
    parser.add_argument("--company-phone", default=None)
    parser.add_argument("--notification-email", default=None)
    parser.add_argument("--trade", default=None, help="Industry pack, e.g. skh")
    parser.add_argument(
        "--company-slug",
        default=None,
        help="Fixed company slug for PILOT_COMPANY_SLUG / public business site",
    )
    parser.add_argument("--admin-first-name", default="Pilot")
    parser.add_argument("--admin-last-name", default="Owner")
    parser.add_argument("--admin-email", required=True)
    parser.add_argument("--admin-password", default=None)
    parser.add_argument("--api-base-url", default="http://localhost:8000")
    parser.add_argument("--frontend-base-url", default="http://localhost:3000")
    args = parser.parse_args()

    admin_password = args.admin_password or _generate_password()
    if not args.admin_password:
        admin_password = getpass.getpass(
            "Admin password (leave blank to auto-generate): ",
        ) or admin_password

    session = SessionLocal()
    try:
        result = setup_pilot_customer(
            company_repository=CompanyRepository(session),
            user_repository=UserRepository(session),
            payload=PilotCustomerInput(
                company_name=args.company_name,
                company_email=args.company_email,
                company_phone=args.company_phone,
                notification_email=args.notification_email,
                trade=args.trade,
                company_slug=args.company_slug,
                admin_first_name=args.admin_first_name,
                admin_last_name=args.admin_last_name,
                admin_email=args.admin_email,
                admin_password=admin_password,
                api_base_url=args.api_base_url,
                frontend_base_url=args.frontend_base_url,
            ),
        )
    finally:
        session.close()

    print(result.message)
    print()
    print("Company")
    print(f"  Name: {result.company_name}")
    print(f"  Slug: {result.company_slug}")
    print(f"  Email: {result.company_email}")
    print(f"  Notification email: {result.notification_email or result.company_email}")
    print()
    print("Admin login")
    print(f"  Email: {result.admin_email}")
    print(f"  Password: {result.admin_password}")
    print()
    print("Widget embed snippet")
    print(result.widget_snippet)


if __name__ == "__main__":
    main()
