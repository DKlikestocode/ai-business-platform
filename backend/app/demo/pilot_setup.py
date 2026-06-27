from dataclasses import dataclass

from pydantic import BaseModel, Field

from app.core.security import hash_password
from app.db.models.enums import UserRole
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository


class PilotCustomerSetupResult(BaseModel):
    company_id: str
    company_name: str
    company_slug: str
    company_email: str
    notification_email: str | None
    admin_user_id: str
    admin_email: str
    admin_password: str
    message: str
    widget_snippet: str = Field(default="")


@dataclass(frozen=True)
class PilotCustomerInput:
    company_name: str
    company_email: str
    company_phone: str | None
    notification_email: str | None
    admin_first_name: str
    admin_last_name: str
    admin_email: str
    admin_password: str
    trade: str | None = None
    api_base_url: str = "http://localhost:8000"
    frontend_base_url: str = "http://localhost:3000"


def setup_pilot_customer(
    *,
    company_repository: CompanyRepository,
    user_repository: UserRepository,
    payload: PilotCustomerInput,
) -> PilotCustomerSetupResult:
    if user_repository.email_exists(payload.admin_email):
        raise ValueError(f"User with email '{payload.admin_email}' already exists.")

    company = company_repository.create(
        name=payload.company_name,
        email=payload.company_email,
        phone=payload.company_phone,
    )

    if payload.notification_email:
        company = company_repository.update_settings(
            company,
            notification_email=payload.notification_email,
        )

    if payload.trade:
        company = company_repository.update_settings(
            company,
            trade=payload.trade,
        )

    user = user_repository.create(
        company_id=company.id,
        first_name=payload.admin_first_name,
        last_name=payload.admin_last_name,
        email=payload.admin_email,
        password_hash=hash_password(payload.admin_password),
        role=UserRole.OWNER,
    )

    api_base = payload.api_base_url.rstrip("/")
    widget_snippet = (
        f'<div\n'
        f'  id="ai-agent-widget"\n'
        f'  data-company-slug="{company.slug}"\n'
        f'  data-api-base="{api_base}"\n'
        f'  data-title="Chat mit uns"\n'
        f'></div>\n'
        f'<script src="{api_base}/static/widget/widget.js"></script>'
    )

    return PilotCustomerSetupResult(
        company_id=str(company.id),
        company_name=company.name,
        company_slug=company.slug,
        company_email=company.email,
        notification_email=company.notification_email,
        admin_user_id=str(user.id),
        admin_email=user.email,
        admin_password=payload.admin_password,
        message=(
            f"Pilot customer '{company.name}' is ready. "
            f"Sign in at {payload.frontend_base_url.rstrip('/')}/login"
        ),
        widget_snippet=widget_snippet,
    )
