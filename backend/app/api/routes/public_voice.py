from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.agents.lead_agent.models import LeadMessageRequest
from app.agents.lead_agent.service import LeadCaptureService
from app.api.dependencies import (
    RateLimit,
    get_company_repository,
    get_voice_lead_capture_service,
)
from app.api.schemas.voice import VoiceMessageRequest, VoiceMessageResponse
from app.api.voice_vapi import (
    build_vapi_tool_results,
    build_voice_request_from_vapi_payload,
    iter_tool_calls,
)
from app.repositories.company_repository import CompanyRepository

router = APIRouter(prefix="/public", tags=["public-voice"])

_voice_rate_limit = RateLimit(limit=60, window_seconds=60, scope="public_voice")


async def _handle_voice_message(
    payload: VoiceMessageRequest,
    *,
    service: LeadCaptureService,
    company_repository: CompanyRepository,
) -> VoiceMessageResponse:
    company = company_repository.get_by_slug(payload.company_slug)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{payload.company_slug}' not found.",
        )

    lead_request = LeadMessageRequest(
        conversation_id=payload.conversation_id,
        message=payload.message,
    )
    lead_response = await service.handle_message(
        lead_request,
        company_id=company.id,
        caller_phone=payload.caller_phone,
    )
    return VoiceMessageResponse(reply=lead_response.reply)


@router.post(
    "/voice/message",
    response_model=VoiceMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a transcribed phone utterance from Vapi",
    dependencies=[Depends(_voice_rate_limit)],
)
async def send_voice_message(
    payload: VoiceMessageRequest,
    service: LeadCaptureService = Depends(get_voice_lead_capture_service),
    company_repository: CompanyRepository = Depends(get_company_repository),
) -> VoiceMessageResponse:
    return await _handle_voice_message(
        payload,
        service=service,
        company_repository=company_repository,
    )


@router.post(
    "/voice/webhook",
    status_code=status.HTTP_200_OK,
    summary="Vapi server URL webhook for phone intake",
    dependencies=[Depends(_voice_rate_limit)],
    response_model=None,
)
async def handle_voice_webhook(
    payload: dict[str, Any],
    service: LeadCaptureService = Depends(get_voice_lead_capture_service),
    company_repository: CompanyRepository = Depends(get_company_repository),
) -> dict[str, Any] | Response:
    message = payload.get("message")
    if not isinstance(message, dict):
        return {}

    message_type = message.get("type")
    if message_type == "end-of-call-report":
        return {}

    if message_type != "tool-calls":
        return {}

    voice_request = build_voice_request_from_vapi_payload(payload)
    if voice_request is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not parse voice tool call payload.",
        )

    voice_response = await _handle_voice_message(
        voice_request,
        service=service,
        company_repository=company_repository,
    )
    tool_results = build_vapi_tool_results(
        iter_tool_calls(message),
        reply=voice_response.reply,
    )
    if not tool_results["results"]:
        return {"reply": voice_response.reply}
    return tool_results


@router.post(
    "/voice/end-of-call",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Optional Vapi end-of-call hook (leads finalize during the call)",
    dependencies=[Depends(_voice_rate_limit)],
)
async def handle_voice_end_of_call() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
