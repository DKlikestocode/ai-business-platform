from datetime import datetime
from uuid import UUID

from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.db.models.company import Company
from app.services.notifications.email_delivery import EmailDeliveryStatus


class CompanyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    email: str
    phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanySettingsResponse(BaseModel):
    name: str
    slug: str
    email: str
    phone: str | None
    notification_email: str | None
    notification_min_urgency: Literal["high", "medium", "low"]
    service_area_center: str | None
    service_radius_km: int | None
    email_delivery_provider: str
    email_delivery_ready: bool
    email_delivery_sends_real_email: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanySettingsUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    notification_email: EmailStr | None = None
    notification_min_urgency: Literal["high", "medium", "low"] | None = None
    service_area_center: str | None = Field(default=None, max_length=255)
    service_radius_km: int | None = Field(default=None, ge=1, le=500)


def company_to_response(company: Company) -> CompanyResponse:
    return CompanyResponse.model_validate(company)


def company_to_settings_response(
    company: Company,
    *,
    email_delivery: EmailDeliveryStatus | None = None,
) -> CompanySettingsResponse:
    delivery = email_delivery or EmailDeliveryStatus(
        provider="logging",
        ready=False,
        sends_real_email=False,
    )
    return CompanySettingsResponse(
        name=company.name,
        slug=company.slug,
        email=company.email,
        phone=company.phone,
        notification_email=company.notification_email,
        notification_min_urgency=company.notification_min_urgency,  # type: ignore[arg-type]
        service_area_center=company.service_area_center,
        service_radius_km=company.service_radius_km,
        created_at=company.created_at,
        **delivery.as_dict(),
    )
