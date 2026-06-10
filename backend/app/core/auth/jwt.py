from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from app.config import Settings

TOKEN_TYPE = "bearer"


def create_access_token(*, user_id: UUID, settings: Settings) -> tuple[str, int]:
    """Create a signed JWT access token and return it with expiry in seconds."""
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expires_at = datetime.now(UTC) + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expires_at,
        "type": TOKEN_TYPE,
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token, int(expires_delta.total_seconds())


def decode_access_token(token: str, settings: Settings) -> UUID:
    """Decode and validate a JWT access token, returning the user ID."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError as exc:
        raise InvalidTokenError("Invalid access token.") from exc

    subject = payload.get("sub")
    if not subject:
        raise InvalidTokenError("Token subject is missing.")

    token_type = payload.get("type")
    if token_type != TOKEN_TYPE:
        raise InvalidTokenError("Invalid token type.")

    try:
        return UUID(str(subject))
    except ValueError as exc:
        raise InvalidTokenError("Token subject is invalid.") from exc
