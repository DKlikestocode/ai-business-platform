from app.config import get_settings
from app.db.models.company import Company
from app.repositories.company_activation_repository import CompanyActivationRepository
from app.repositories.company_repository import CompanyRepository


def test_get_public_business_site_returns_profile_and_widget_config(client, db_session):
    settings = get_settings()
    company_repo = CompanyRepository(db_session)
    company = company_repo.create(
        name="Meister Müller Sanitär",
        email="kontakt@mueller.de",
        phone="+49 40 123456",
    )
    company = company_repo.update_settings(
        company,
        trade="skh",
        service_area_center="22303 Hamburg",
        service_radius_km=30,
    )
    activation = CompanyActivationRepository(db_session).get_or_create(company.id)

    response = client.get(f"/api/v1/public/site/{company.slug}")

    assert response.status_code == 200
    body = response.json()
    assert body["company_name"] == "Meister Müller Sanitär"
    assert body["company_slug"] == company.slug
    assert body["email"] == "kontakt@mueller.de"
    assert body["phone"] == "+49 40 123456"
    assert body["trade"] == "skh"
    assert body["service_area_center"] == "22303 Hamburg"
    assert body["service_radius_km"] == 30
    assert body["widget_company_slug"] == company.slug
    assert body["widget_install_token"] == activation.install_token
    assert body["widget_api_base"] == settings.public_api_base_url.rstrip("/")


def test_get_public_business_site_unknown_slug_returns_404(client):
    response = client.get("/api/v1/public/site/unknown-slug")

    assert response.status_code == 404
