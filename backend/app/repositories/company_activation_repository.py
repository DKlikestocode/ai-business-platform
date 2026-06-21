import secrets
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.company_activation import CompanyActivation
from app.db.models.enums import ActivationStatus


class CompanyActivationRepository:
    """Persistence layer for tenant activation state."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_company_id(self, company_id: UUID) -> CompanyActivation | None:
        return self._session.get(CompanyActivation, company_id)

    def create(self, company_id: UUID, *, install_token: str) -> CompanyActivation:
        activation = CompanyActivation(
            company_id=company_id,
            install_token=install_token,
            status=ActivationStatus.AWAITING_WIDGET.value,
        )
        self._session.add(activation)
        self._session.commit()
        self._session.refresh(activation)
        return activation

    def get_or_create(self, company_id: UUID) -> CompanyActivation:
        existing = self.get_by_company_id(company_id)
        if existing is not None:
            return existing

        install_token = secrets.token_urlsafe(32)
        try:
            return self.create(company_id, install_token=install_token)
        except IntegrityError:
            self._session.rollback()
            existing = self.get_by_company_id(company_id)
            if existing is None:
                raise
            return existing

    def update_website_url(
        self,
        activation: CompanyActivation,
        *,
        website_url: str | None,
    ) -> CompanyActivation:
        activation.website_url = website_url
        self._session.commit()
        self._session.refresh(activation)
        return activation

    def record_heartbeat(
        self,
        activation: CompanyActivation,
        *,
        page_origin: str,
        seen_at: datetime | None = None,
    ) -> CompanyActivation:
        timestamp = seen_at or datetime.now(UTC)
        activation.status = ActivationStatus.LIVE.value
        if activation.widget_live_at is None:
            activation.widget_live_at = timestamp
        activation.widget_last_seen_at = timestamp
        activation.widget_last_origin = page_origin
        self._session.commit()
        self._session.refresh(activation)
        return activation

    def record_first_website_inquiry(
        self,
        company_id: UUID,
        *,
        lead_id: UUID,
        inquired_at: datetime | None = None,
    ) -> bool:
        """Persist the first website inquiry milestone when not yet recorded."""
        activation = self.get_or_create(company_id)
        if activation.first_website_inquiry_at is not None:
            return False

        activation.first_website_inquiry_at = inquired_at or datetime.now(UTC)
        activation.first_website_inquiry_lead_id = lead_id
        self._session.commit()
        self._session.refresh(activation)
        return True
