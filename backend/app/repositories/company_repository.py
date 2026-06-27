from uuid import UUID

from sqlalchemy.orm import Session

from app.core.utils import slugify
from app.db.models.company import Company
from app.services.service_area.coordinates import refresh_company_service_area_coordinates


class CompanyRepository:
    """Persistence layer for tenant companies."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        name: str,
        email: str,
        phone: str | None = None,
        slug: str | None = None,
    ) -> Company:
        company = Company(
            name=name,
            slug=slug or self._generate_unique_slug(name),
            email=email,
            phone=phone,
        )
        self._session.add(company)
        self._session.commit()
        self._session.refresh(company)
        return company

    def get_by_id(self, company_id: UUID) -> Company | None:
        return self._session.get(Company, company_id)

    def get_by_slug(self, slug: str) -> Company | None:
        return self._session.query(Company).filter(Company.slug == slug).one_or_none()

    def slug_exists(self, slug: str, *, exclude_company_id: UUID | None = None) -> bool:
        company = self.get_by_slug(slug)
        if company is None:
            return False
        if exclude_company_id is not None and company.id == exclude_company_id:
            return False
        return True

    def update_settings(self, company: Company, **fields: object) -> Company:
        service_area_changed = any(
            key in fields
            for key in ("service_area_center", "service_radius_km")
        )

        for key, value in fields.items():
            setattr(company, key, value)

        if service_area_changed:
            refresh_company_service_area_coordinates(company)

        self._session.commit()
        self._session.refresh(company)
        return company

    def _generate_unique_slug(
        self,
        name: str,
        *,
        exclude_company_id: UUID | None = None,
    ) -> str:
        base_slug = slugify(name)
        slug = base_slug
        suffix = 1
        while self.slug_exists(slug, exclude_company_id=exclude_company_id):
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        return slug
