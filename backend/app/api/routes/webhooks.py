import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.api.dependencies import (
    get_company_repository,
    get_intake_service,
    get_resend_received_email_client,
    get_resend_webhook_verifier,
)
from app.api.schemas.webhooks import ResendWebhookAcceptedResponse
from app.config import Settings, get_settings
from app.repositories.company_repository import CompanyRepository
from app.services.intake.email_parser import EmailParseError
from app.services.intake.resend import (
    ResendFetchError,
    ResendReceivedEmailClient,
    ResendWebhookVerificationError,
    ResendWebhookVerifier,
    extract_received_email_id,
    resolve_company_slug,
)
from app.services.intake.service import IntakeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
MAX_WEBHOOK_BYTES = 1024 * 1024


@router.post(
    "/resend",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ResendWebhookAcceptedResponse,
    summary="Receive an authenticated Resend inbound email event",
)
async def receive_resend_email(
    request: Request,
    settings: Settings = Depends(get_settings),
    verifier: ResendWebhookVerifier = Depends(get_resend_webhook_verifier),
    resend_client: ResendReceivedEmailClient = Depends(
        get_resend_received_email_client
    ),
    company_repository: CompanyRepository = Depends(get_company_repository),
    intake_service: IntakeService = Depends(get_intake_service),
) -> ResendWebhookAcceptedResponse | Response:
    if not settings.intake_email_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inbound email intake is disabled.",
        )

    raw_body = await _read_limited_body(request)
    try:
        event = verifier.verify(raw_body, request.headers)
    except ResendWebhookVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature.",
        ) from exc

    if event.get("type") != "email.received":
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    email_id = extract_received_email_id(event)
    company_slug = resolve_company_slug(
        event,
        inbound_domain=settings.resend_inbound_domain,
    )
    if email_id is None or company_slug is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Inbound email event is missing its email ID or recipient.",
        )

    company = company_repository.get_by_slug(company_slug)
    if company is None:
        logger.warning("Ignored inbound email for unknown company slug")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    try:
        raw_message = await resend_client.retrieve_raw_message(email_id)
        result = await intake_service.ingest_email(
            company_id=company.id,
            raw_message=raw_message,
            provider_event_id=request.headers.get("svix-id"),
        )
    except ResendFetchError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The received email could not be retrieved.",
        ) from exc
    except EmailParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The received message is not a supported email.",
        ) from exc

    return ResendWebhookAcceptedResponse(
        accepted=True,
        created=result.created,
        intake_item_id=result.item.id,
    )


async def _read_limited_body(request: Request) -> bytes:
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_WEBHOOK_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail="Webhook payload is too large.",
                )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Content-Length header.",
            ) from exc

    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_WEBHOOK_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Webhook payload is too large.",
            )
    return bytes(body)
