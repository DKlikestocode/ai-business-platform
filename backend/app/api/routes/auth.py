from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import RateLimit, get_auth_service, get_current_user
from app.api.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    TokenResponse,
    current_user_to_response,
)
from app.db.models.user import User
from app.domain.exceptions import AuthenticationError
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

_AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}
_login_rate_limit = RateLimit(limit=10, window_seconds=60, scope="auth_login")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with email and password",
    dependencies=[Depends(_login_rate_limit)],
)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        user = service.authenticate(email=str(payload.email), password=payload.password)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers=_AUTH_HEADERS,
        ) from exc

    access_token, token_type, expires_in = service.issue_access_token(user)
    return TokenResponse(
        access_token=access_token,
        token_type=token_type,
        expires_in=expires_in,
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Get the authenticated user",
)
def get_me(current_user: User = Depends(get_current_user)) -> CurrentUserResponse:
    return current_user_to_response(current_user)
