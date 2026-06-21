from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.db.models.company import Company


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
    notify_on_new_lead: bool
    notify_on_contactable_lead: bool
    contactable_lead_notification_threshold: int
    service_area_center: str | None
    service_radius_km: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanySettingsUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    notification_email: EmailStr | None = None
    notify_on_new_lead: bool | None = None
    notify_on_contactable_lead: bool | None = None
    contactable_lead_notification_threshold: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    service_area_center: str | None = Field(default=None, max_length=255)
    service_radius_km: int | None = Field(default=None, ge=1, le=500)


def company_to_response(company: Company) -> CompanyResponse:
    return CompanyResponse.model_validate(company)


def company_to_settings_response(company: Company) -> CompanySettingsResponse:
    return CompanySettingsResponse.model_validate(company)
