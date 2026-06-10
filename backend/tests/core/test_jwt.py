from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from app.config import Settings
from app.core.auth.jwt import TOKEN_TYPE, create_access_token, decode_access_token


@pytest.fixture
def auth_settings() -> Settings:
    return Settings(
        jwt_secret_key="test-secret-key",
        jwt_algorithm="HS256",
        access_token_expire_minutes=15,
    )


def test_create_and_decode_access_token_round_trip(auth_settings: Settings) -> None:
    user_id = uuid4()

    token, expires_in = create_access_token(user_id=user_id, settings=auth_settings)

    assert token
    assert expires_in == 15 * 60
    assert decode_access_token(token, auth_settings) == user_id


def test_decode_access_token_rejects_expired_token(auth_settings: Settings) -> None:
    user_id = uuid4()
    expired_at = datetime.now(UTC) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": str(user_id), "exp": expired_at, "type": TOKEN_TYPE},
        auth_settings.jwt_secret_key,
        algorithm=auth_settings.jwt_algorithm,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token, auth_settings)


def test_decode_access_token_rejects_wrong_token_type(auth_settings: Settings) -> None:
    user_id = uuid4()
    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "type": "refresh",
        },
        auth_settings.jwt_secret_key,
        algorithm=auth_settings.jwt_algorithm,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token, auth_settings)
