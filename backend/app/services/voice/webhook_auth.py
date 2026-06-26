import secrets

from fastapi import HTTPException, status

from app.config import Settings


def require_vapi_webhook_secret(header_value: str | None, settings: Settings) -> None:
    configured = settings.vapi_webhook_secret.strip()
    if not configured:
        return
    if header_value is None or not secrets.compare_digest(header_value, configured):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid voice webhook secret.",
        )
