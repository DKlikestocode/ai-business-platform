import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.password_reset_token import PasswordResetToken


class PasswordResetRepository:
    """Persistence for one-time password reset tokens."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def create_token(
        self,
        *,
        user_id: UUID,
        expires_in_minutes: int = 60,
    ) -> tuple[PasswordResetToken, str]:
        raw_token = secrets.token_urlsafe(32)
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=self.hash_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(minutes=expires_in_minutes),
        )
        self._session.add(token)
        self._session.commit()
        self._session.refresh(token)
        return token, raw_token

    def get_valid_token(self, raw_token: str) -> PasswordResetToken | None:
        token_hash = self.hash_token(raw_token)
        token = (
            self._session.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash)
            .one_or_none()
        )
        if token is None:
            return None
        if token.used_at is not None:
            return None
        if token.expires_at <= datetime.now(UTC):
            return None
        return token

    def mark_used(self, token: PasswordResetToken) -> None:
        token.used_at = datetime.now(UTC)
        self._session.commit()

    def invalidate_active_tokens_for_user(self, user_id: UUID) -> None:
        now = datetime.now(UTC)
        (
            self._session.query(PasswordResetToken)
            .filter(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .update({PasswordResetToken.used_at: now}, synchronize_session=False)
        )
        self._session.commit()
