from uuid import UUID

from app.domain.exceptions import ConflictError, NotFoundError
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password
from app.db.models.company import Company
from app.db.models.enums import UserRole
from app.db.models.user import User


class CompanyService:
    """Business logic for company management."""

    def __init__(self, repository: CompanyRepository) -> None:
        self._repository = repository

    def create_company(
        self,
        *,
        name: str,
        email: str,
        phone: str | None = None,
    ) -> Company:
        return self._repository.create(name=name, email=email, phone=phone)

    def get_company(self, company_id: UUID) -> Company:
        company = self._repository.get_by_id(company_id)
        if company is None:
            raise NotFoundError(f"Company '{company_id}' not found.")
        return company

    def get_settings(self, company_id: UUID) -> Company:
        return self.get_company(company_id)

    def update_settings(
        self,
        company_id: UUID,
        *,
        updates: dict[str, object],
    ) -> Company:
        company = self.get_company(company_id)
        if not updates:
            return company
        return self._repository.update_settings(company, **updates)


class UserService:
    """Business logic for user management."""

    def __init__(
        self,
        user_repository: UserRepository,
        company_repository: CompanyRepository,
    ) -> None:
        self._user_repository = user_repository
        self._company_repository = company_repository

    def create_user(
        self,
        *,
        company_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        role: UserRole = UserRole.MEMBER,
    ) -> User:
        if self._company_repository.get_by_id(company_id) is None:
            raise NotFoundError(f"Company '{company_id}' not found.")

        if self._user_repository.email_exists(email):
            raise ConflictError(f"User with email '{email}' already exists.")

        password_hash = hash_password(password)
        return self._user_repository.create(
            company_id=company_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role=role,
        )
