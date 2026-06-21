from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.enums import UserRole
from app.db.models.user import User


class UserRepository:
    """Persistence layer for company users."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        company_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.MEMBER,
        is_active: bool = True,
    ) -> User:
        user = User(
            company_id=company_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role=role.value,
            is_active=is_active,
        )
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._session.query(User).filter(User.email == email).one_or_none()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def update_password(self, user: User, *, password_hash: str) -> User:
        user.password_hash = password_hash
        self._session.commit()
        self._session.refresh(user)
        return user
