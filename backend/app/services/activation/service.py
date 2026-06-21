import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.db.models.company import Company
from app.db.models.company_activation import CompanyActivation
from app.db.models.enums import ActivationStatus
from app.domain.exceptions import InvalidWidgetHeartbeatError, NotFoundError
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository
from app.services.activation.embed import build_widget_embed_snippet
from app.services.activation.origin import (
    InvalidPageOriginError,
    build_blocked_origins,
    validate_widget_page_origin,
)
from app.services.notifications.recipient import is_notification_configured


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
    first_website_inquiry_at: str | None
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
        frontend_base_url: str | None = None,
        cors_origins: list[str] | None = None,
        widget_stale_after_hours: int = 168,
    ) -> None:
        self._company_repository = company_repository
        self._activation_repository = activation_repository
        self._public_api_base_url = public_api_base_url.rstrip("/")
        self._widget_stale_after_hours = widget_stale_after_hours
        self._blocked_origins = build_blocked_origins(
            public_api_base_url=public_api_base_url,
            frontend_base_url=frontend_base_url,
            cors_origins=cors_origins or [],
        )

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

    def record_widget_heartbeat(
        self,
        *,
        company_slug: str,
        install_token: str,
        page_origin: str,
        widget_version: str | None = None,
    ) -> None:
        del widget_version

        try:
            normalized_origin = validate_widget_page_origin(
                page_origin,
                blocked_origins=self._blocked_origins,
            )
        except InvalidPageOriginError:
            raise InvalidWidgetHeartbeatError from None

        company = self._company_repository.get_by_slug(company_slug)
        if company is None:
            raise InvalidWidgetHeartbeatError

        activation = self._activation_repository.get_by_company_id(company.id)
        if activation is None:
            raise InvalidWidgetHeartbeatError

        if not secrets.compare_digest(install_token, activation.install_token):
            raise InvalidWidgetHeartbeatError

        self._activation_repository.record_heartbeat(
            activation,
            page_origin=normalized_origin,
        )

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
            first_website_inquiry_at=self._format_datetime(
                activation.first_website_inquiry_at,
            ),
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
        return is_notification_configured(company)

    def _effective_status(
        self,
        company: Company,
        activation: CompanyActivation,
    ) -> ActivationStatus:
        if not self._notification_configured(company):
            return ActivationStatus.SETUP_INCOMPLETE

        persisted_status = activation.status_enum
        if persisted_status != ActivationStatus.LIVE:
            return persisted_status

        if self._widget_heartbeat_is_stale(activation):
            return ActivationStatus.STALE

        return ActivationStatus.LIVE

    def _widget_heartbeat_is_stale(self, activation: CompanyActivation) -> bool:
        last_seen = activation.widget_last_seen_at
        if last_seen is None:
            return False

        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=UTC)

        age = datetime.now(UTC) - last_seen
        return age > timedelta(hours=self._widget_stale_after_hours)

    @staticmethod
    def _format_datetime(value: object | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()  # type: ignore[union-attr]
