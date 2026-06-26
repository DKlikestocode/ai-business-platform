import json
from typing import Any

from app.api.schemas.voice import VoiceMessageRequest

_VOICE_TOOL_NAMES = frozenset(
    {
        "capture_inquiry",
        "handle_user_message",
        "process_user_message",
    }
)


def extract_company_slug(call: dict[str, Any]) -> str | None:
    for container in (
        call.get("metadata") or {},
        (call.get("assistantOverrides") or {}).get("metadata") or {},
        (call.get("assistant") or {}).get("metadata") or {},
    ):
        slug = container.get("company_slug")
        if isinstance(slug, str) and slug.strip():
            return slug.strip()
    return None


def extract_caller_phone(call: dict[str, Any]) -> str | None:
    customer = call.get("customer") or {}
    number = customer.get("number")
    if isinstance(number, str) and number.strip():
        return number.strip()
    return None


def extract_conversation_id(call: dict[str, Any]) -> str | None:
    call_id = call.get("id")
    if isinstance(call_id, str) and call_id.strip():
        return call_id.strip()
    return None


def iter_tool_calls(message: dict[str, Any]) -> list[dict[str, Any]]:
    tool_calls: list[dict[str, Any]] = []
    for key in ("toolCallList", "toolCalls", "toolWithToolCallList"):
        entries = message.get(key)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if "toolCall" in entry and isinstance(entry["toolCall"], dict):
                tool_calls.append(entry["toolCall"])
            else:
                tool_calls.append(entry)
    return tool_calls


def parse_voice_message_from_tool_call(
    tool_call: dict[str, Any],
    *,
    fallback_message: str | None = None,
) -> str | None:
    function = tool_call.get("function") or {}
    raw_arguments = function.get("arguments")
    if isinstance(raw_arguments, dict):
        arguments = raw_arguments
    elif isinstance(raw_arguments, str) and raw_arguments.strip():
        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError:
            arguments = {}
    else:
        arguments = {}

    for key in ("message", "user_message", "transcript", "text"):
        value = arguments.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    if fallback_message and fallback_message.strip():
        return fallback_message.strip()
    return None


def build_voice_request_from_vapi_payload(
    payload: dict[str, Any],
) -> VoiceMessageRequest | None:
    message = payload.get("message")
    if not isinstance(message, dict):
        return None

    call = message.get("call")
    if not isinstance(call, dict):
        return None

    company_slug = extract_company_slug(call)
    conversation_id = extract_conversation_id(call)
    if company_slug is None or conversation_id is None:
        return None

    fallback_message = message.get("transcript") or message.get("text")
    if not isinstance(fallback_message, str):
        fallback_message = None

    user_message: str | None = None
    for tool_call in iter_tool_calls(message):
        function = tool_call.get("function") or {}
        if function.get("name") not in _VOICE_TOOL_NAMES:
            continue
        user_message = parse_voice_message_from_tool_call(
            tool_call,
            fallback_message=fallback_message,
        )
        if user_message:
            break

    if user_message is None and isinstance(fallback_message, str) and fallback_message.strip():
        user_message = fallback_message.strip()

    if user_message is None:
        return None

    return VoiceMessageRequest(
        company_slug=company_slug,
        conversation_id=conversation_id,
        message=user_message,
        caller_phone=extract_caller_phone(call),
    )


def build_vapi_tool_results(
    tool_calls: list[dict[str, Any]],
    *,
    reply: str,
) -> dict[str, list[dict[str, str]]]:
    results: list[dict[str, str]] = []
    for tool_call in tool_calls:
        function = tool_call.get("function") or {}
        if function.get("name") not in _VOICE_TOOL_NAMES:
            continue
        tool_call_id = tool_call.get("id")
        if not isinstance(tool_call_id, str) or not tool_call_id:
            continue
        results.append({"toolCallId": tool_call_id, "result": reply})
    return {"results": results}
