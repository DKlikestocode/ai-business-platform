import logging

from app.config import Settings
from app.core.auth.jwt import TOKEN_TYPE, create_access_token
from app.core.security import hash_password, verify_password
from app.db.models.user import User
from app.domain.exceptions import AuthenticationError
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.user_repository import UserRepository
from app.services.notifications.interface import EmailMessage
from app.services.notifications.service import NotificationService

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and token issuance."""

    def __init__(
        self,
        user_repository: UserRepository,
        settings: Settings,
        *,
        password_reset_repository: PasswordResetRepository | None = None,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._settings = settings
        self._password_reset_repository = password_reset_repository
        self._notification_service = notification_service

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

    async def request_password_reset(self, *, email: str) -> None:
        if self._password_reset_repository is None or self._notification_service is None:
            logger.warning("Password reset requested but dependencies are not configured.")
            return

        user = self._user_repository.get_by_email(email)
        if user is None or not user.is_active:
            return

        self._password_reset_repository.invalidate_active_tokens_for_user(user.id)
        _token, raw_token = self._password_reset_repository.create_token(user_id=user.id)
        reset_url = self._build_password_reset_url(raw_token)
        await self._notification_service.send_password_reset_email(
            to=user.email,
            reset_url=reset_url,
        )

    def reset_password(self, *, token: str, password: str) -> None:
        if self._password_reset_repository is None:
            raise AuthenticationError("Password reset is not available.")

        reset_token = self._password_reset_repository.get_valid_token(token)
        if reset_token is None:
            raise AuthenticationError("Invalid or expired reset link.")

        user = self._user_repository.get_by_id(reset_token.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid or expired reset link.")

        password_hash = hash_password(password)
        self._user_repository.update_password(user, password_hash=password_hash)
        self._password_reset_repository.mark_used(reset_token)
        self._password_reset_repository.invalidate_active_tokens_for_user(user.id)

    def _build_password_reset_url(self, raw_token: str) -> str:
        base_url = (self._settings.frontend_base_url or "http://localhost:3000").rstrip("/")
        return f"{base_url}/reset-password?token={raw_token}"
