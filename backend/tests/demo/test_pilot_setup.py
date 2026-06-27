import uuid

import pytest

from app.demo.pilot_setup import PilotCustomerInput, setup_pilot_customer


def test_setup_pilot_customer_creates_company_and_owner(
    company_repository,
    user_repository,
) -> None:
    suffix = uuid.uuid4().hex[:8]
    result = setup_pilot_customer(
        company_repository=company_repository,
        user_repository=user_repository,
        payload=PilotCustomerInput(
            company_name=f"Pilot Co {suffix}",
            company_email=f"pilot-{suffix}@example.com",
            company_phone="+49 30 123456",
            notification_email=f"alerts-{suffix}@example.com",
            admin_first_name="Pilot",
            admin_last_name="Owner",
            admin_email=f"owner-{suffix}@example.com",
            admin_password="secure-password",
        ),
    )

    assert result.company_slug
    assert result.notification_email == f"alerts-{suffix}@example.com"
    assert result.admin_email == f"owner-{suffix}@example.com"
    assert 'data-company-slug="' in result.widget_snippet
    assert "/static/widget/widget.js" in result.widget_snippet


def test_setup_pilot_customer_sets_trade_when_provided(
    company_repository,
    user_repository,
) -> None:
    suffix = uuid.uuid4().hex[:8]
    result = setup_pilot_customer(
        company_repository=company_repository,
        user_repository=user_repository,
        payload=PilotCustomerInput(
            company_name=f"SKH Pilot {suffix}",
            company_email=f"skh-{suffix}@example.com",
            company_phone=None,
            notification_email=None,
            trade="skh",
            admin_first_name="Pilot",
            admin_last_name="Owner",
            admin_email=f"skh-owner-{suffix}@example.com",
            admin_password="secure-password",
        ),
    )

    company = company_repository.get_by_slug(result.company_slug)
    assert company is not None
    assert company.trade == "skh"


def test_setup_pilot_customer_rejects_duplicate_admin_email(
    company_repository,
    user_repository,
) -> None:
    suffix = uuid.uuid4().hex[:8]
    email = f"duplicate-{suffix}@example.com"
    payload = PilotCustomerInput(
        company_name=f"Pilot Co {suffix}",
        company_email=f"pilot-{suffix}@example.com",
        company_phone=None,
        notification_email=None,
        admin_first_name="Pilot",
        admin_last_name="Owner",
        admin_email=email,
        admin_password="secure-password",
    )

    setup_pilot_customer(
        company_repository=company_repository,
        user_repository=user_repository,
        payload=payload,
    )

    with pytest.raises(ValueError, match="already exists"):
        setup_pilot_customer(
            company_repository=company_repository,
            user_repository=user_repository,
            payload=PilotCustomerInput(
                company_name=f"Other Co {suffix}",
                company_email=f"other-{suffix}@example.com",
                company_phone=None,
                notification_email=None,
                admin_first_name="Other",
                admin_last_name="Owner",
                admin_email=email,
                admin_password="secure-password",
            ),
        )
