from pydantic import BaseModel


class PublicBusinessSiteResponse(BaseModel):
    company_name: str
    company_slug: str
    email: str
    phone: str | None
    trade: str | None
    service_area_center: str | None
    service_radius_km: int | None
    widget_company_slug: str
    widget_api_base: str
    widget_install_token: str
    widget_title: str = "Anfrage senden"
