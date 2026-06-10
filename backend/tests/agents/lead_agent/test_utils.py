import pytest

from app.agents.lead_agent.models import LeadCaptureLLMOutput, LeadExtractedData
from app.agents.lead_agent.utils import (
    get_missing_fields,
    is_lead_complete,
    merge_lead_data,
)


def test_merge_lead_data_preserves_existing_and_adds_new_fields() -> None:
    existing = LeadExtractedData(name="Jane Doe", phone="+1 555 0100")
    incoming = LeadExtractedData(location="Austin, TX", service_requested="Roof repair")

    merged = merge_lead_data(existing, incoming)

    assert merged.name == "Jane Doe"
    assert merged.phone == "+1 555 0100"
    assert merged.location == "Austin, TX"
    assert merged.service_requested == "Roof repair"


def test_get_missing_fields_returns_required_only() -> None:
    data = LeadExtractedData(
        name="Jane",
        phone="555",
        location="Austin",
    )

    missing = get_missing_fields(data)

    assert "name" not in missing
    assert "phone" not in missing
    assert "service_requested" in missing
    assert "description" in missing
    assert "urgency" in missing
    assert "preferred_callback_time" in missing
    assert "email" not in missing


def test_is_lead_complete_when_all_required_fields_present() -> None:
    data = LeadExtractedData(
        name="Jane",
        phone="555",
        location="Austin",
        service_requested="HVAC",
        description="AC not cooling",
        urgency="high",
        preferred_callback_time="Tomorrow morning",
    )

    assert is_lead_complete(data) is True
