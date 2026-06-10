from app.config import Settings
from app.core.auth.jwt import TOKEN_TYPE, create_access_token
from app.core.security import verify_password
from app.db.models.user import User
from app.domain.exceptions import AuthenticationError
from app.repositories.user_repository import UserRepository


class AuthService:
    """Authentication and token issuance."""

    def __init__(self, user_repository: UserRepository, settings: Settings) -> None:
        self._user_repository = user_repository
        self._settings = settings

    def authenticate(self, *, email: str, password: str) -> User:
        user = self._user_repository.get_by_email(email)
        if user is None:
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("Invalid email or password.")

        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        return user

    def issue_access_token(self, user: User) -> tuple[str, str, int]:
        access_token, expires_in = create_access_token(
            user_id=user.id,
            settings=self._settings,
        )
        return access_token, TOKEN_TYPE, expires_in
