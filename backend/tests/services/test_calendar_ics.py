from datetime import UTC, datetime

from app.agents.lead_agent.models import InquiryKind, LeadExtractedData
from app.agents.lead_agent.appointment import (
    is_appointment_inquiry,
    should_ask_appointment_confirmation_preference,
)
from app.db.models.company import Company
from app.db.models.lead import Lead
from app.services.calendar.ics import (
    build_lead_calendar_ics,
    parse_appointment_window,
)


def _sample_lead(**overrides) -> Lead:
    lead = Lead(
        company_id=overrides.pop("company_id"),
        conversation_id="conv-1",
        name="Max",
        phone="0170",
        email="max@example.com",
        location="Berlin",
        service_requested="Service",
        description="Desc",
        urgency="mittel",
        preferred_callback_time="Morgen 14:30",
        status="new",
        inquiry_kind=InquiryKind.APPOINTMENT_CONSULTATION.value,
    )
    for key, value in overrides.items():
        setattr(lead, key, value)
    return lead


def test_parse_appointment_window_time(company: Company) -> None:
    reference = datetime(2026, 7, 12, 10, 0, tzinfo=UTC)
    window = parse_appointment_window("Morgen 14:30", reference=reference)
    assert window is not None
    assert window.all_day is False
    assert window.start.hour == 14
    assert window.start.minute == 30


def test_build_lead_calendar_ics_contains_event(company: Company) -> None:
    lead = _sample_lead(company_id=company.id, created_at=datetime(2026, 7, 12, 10, 0, tzinfo=UTC))
    ics = build_lead_calendar_ics(company=company, lead=lead, frontend_base_url="https://app.example.com")
    assert "BEGIN:VCALENDAR" in ics
    assert company.name in ics
    assert "Morgen 14:30" in ics


def test_should_ask_appointment_confirmation_preference() -> None:
    data = LeadExtractedData(
        inquiry_kind=InquiryKind.APPOINTMENT_CONSULTATION,
        preferred_callback_time="Donnerstag Vormittag",
    )
    assert is_appointment_inquiry(data) is True
    assert should_ask_appointment_confirmation_preference(data) is False
