from datetime import datetime

from pydantic import BaseModel, Field

from app.db.models.enums import ActivationStatus
from app.services.activation.service import ActivationView


class ActivationInstallResponse(BaseModel):
    company_slug: str
    embed_snippet: str


class ActivationResponse(BaseModel):
    status: ActivationStatus
    notification_configured: bool
    website_url: str | None
    widget_live_at: datetime | None
    widget_last_seen_at: datetime | None
    widget_last_origin: str | None
    install: ActivationInstallResponse
    updated_at: datetime


class ActivationUpdateRequest(BaseModel):
    website_url: str | None = Field(default=None, max_length=2048)


def activation_to_response(view: ActivationView) -> ActivationResponse:
    return ActivationResponse(
        status=view.status,
        notification_configured=view.notification_configured,
        website_url=view.website_url,
        widget_live_at=(
            datetime.fromisoformat(view.widget_live_at)
            if view.widget_live_at
            else None
        ),
        widget_last_seen_at=(
            datetime.fromisoformat(view.widget_last_seen_at)
            if view.widget_last_seen_at
            else None
        ),
        widget_last_origin=view.widget_last_origin,
        install=ActivationInstallResponse(
            company_slug=view.install.company_slug,
            embed_snippet=view.install.embed_snippet,
        ),
        updated_at=datetime.fromisoformat(view.updated_at),
    )
