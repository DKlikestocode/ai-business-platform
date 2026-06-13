from dataclasses import dataclass
from uuid import UUID

from app.db.models.company import Company
from app.db.models.company_activation import CompanyActivation
from app.db.models.enums import ActivationStatus
from app.domain.exceptions import NotFoundError
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.services.activation.embed import build_widget_embed_snippet


@dataclass(frozen=True)
class ActivationInstall:
    company_slug: str
    embed_snippet: str


@dataclass(frozen=True)
class ActivationView:
    status: ActivationStatus
    notification_configured: bool
    website_url: str | None
    widget_live_at: str | None
    widget_last_seen_at: str | None
    widget_last_origin: str | None
    install: ActivationInstall
    updated_at: str


class ActivationService:
    """Business logic for company activation state."""

    def __init__(
        self,
        company_repository: CompanyRepository,
        activation_repository: CompanyActivationRepository,
        *,
        public_api_base_url: str,
    ) -> None:
        self._company_repository = company_repository
        self._activation_repository = activation_repository
        self._public_api_base_url = public_api_base_url.rstrip("/")

    def get_activation(self, company_id: UUID) -> ActivationView:
        company = self._company_repository.get_by_id(company_id)
        if company is None:
            raise NotFoundError(f"Company '{company_id}' not found.")

        activation = self._activation_repository.get_or_create(company_id)
        return self._to_view(company, activation)

    def update_website_url(
        self,
        company_id: UUID,
        *,
        website_url: str | None,
    ) -> ActivationView:
        company = self._company_repository.get_by_id(company_id)
        if company is None:
            raise NotFoundError(f"Company '{company_id}' not found.")

        activation = self._activation_repository.get_or_create(company_id)
        activation = self._activation_repository.update_website_url(
            activation,
            website_url=website_url,
        )
        return self._to_view(company, activation)

    def _to_view(self, company: Company, activation: CompanyActivation) -> ActivationView:
        notification_configured = self._notification_configured(company)
        status = self._effective_status(company, activation)

        return ActivationView(
            status=status,
            notification_configured=notification_configured,
            website_url=activation.website_url,
            widget_live_at=self._format_datetime(activation.widget_live_at),
            widget_last_seen_at=self._format_datetime(activation.widget_last_seen_at),
            widget_last_origin=activation.widget_last_origin,
            install=ActivationInstall(
                company_slug=company.slug,
                embed_snippet=build_widget_embed_snippet(
                    company_slug=company.slug,
                    api_base=self._public_api_base_url,
                    install_token=activation.install_token,
                ),
            ),
            updated_at=activation.updated_at.isoformat(),
        )

    @staticmethod
    def _notification_configured(company: Company) -> bool:
        return bool(company.notification_email and company.notification_email.strip())

    def _effective_status(
        self,
        company: Company,
        activation: CompanyActivation,
    ) -> ActivationStatus:
        if not self._notification_configured(company):
            return ActivationStatus.SETUP_INCOMPLETE
        return activation.status_enum

    @staticmethod
    def _format_datetime(value: object | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()  # type: ignore[union-attr]
