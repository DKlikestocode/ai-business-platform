import json

import pytest

from app.api.voice_vapi import (
    build_voice_request_from_vapi_payload,
    extract_company_slug,
    extract_conversation_id,
)


def test_extract_company_slug_from_call_metadata() -> None:
    call = {"metadata": {"company_slug": "demo-sanitaer"}}
    assert extract_company_slug(call) == "demo-sanitaer"


def test_extract_conversation_id_from_call_id() -> None:
    call = {"id": "vapi-call-abc"}
    assert extract_conversation_id(call) == "vapi-call-abc"


def test_build_voice_request_from_tool_call_payload() -> None:
    payload = {
        "message": {
            "type": "tool-calls",
            "call": {
                "id": "call-123",
                "metadata": {"company_slug": "demo-sanitaer"},
                "customer": {"number": "+491701234567"},
            },
            "toolCallList": [
                {
                    "id": "tool-1",
                    "function": {
                        "name": "capture_inquiry",
                        "arguments": json.dumps({"message": "Wasser im Keller"}),
                    },
                }
            ],
        }
    }

    request = build_voice_request_from_vapi_payload(payload)
    assert request is not None
    assert request.company_slug == "demo-sanitaer"
    assert request.conversation_id == "call-123"
    assert request.message == "Wasser im Keller"
    assert request.caller_phone == "+491701234567"


@pytest.mark.parametrize("missing_key", ["call", "metadata", "toolCallList"])
def test_build_voice_request_returns_none_when_incomplete(missing_key: str) -> None:
    payload = {
        "message": {
            "type": "tool-calls",
            "call": {
                "id": "call-123",
                "metadata": {"company_slug": "demo-sanitaer"},
                "customer": {"number": "+491701234567"},
            },
            "toolCallList": [
                {
                    "id": "tool-1",
                    "function": {
                        "name": "capture_inquiry",
                        "arguments": json.dumps({"message": "Hilfe"}),
                    },
                }
            ],
        }
    }
    if missing_key == "call":
        payload["message"].pop("call")
    elif missing_key == "metadata":
        payload["message"]["call"].pop("metadata")
    else:
        payload["message"].pop("toolCallList")

    assert build_voice_request_from_vapi_payload(payload) is None
