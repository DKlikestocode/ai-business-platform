"""Generate ICS calendar events for appointment inquiries."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

from app.db.models.company import Company
from app.db.models.lead import Lead


@dataclass(frozen=True)
class CalendarEventWindow:
    all_day: bool
    start: datetime
    end: datetime


_TIME_PATTERN = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")


def _escape_ics_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _format_ics_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _format_ics_date(value: date) -> str:
    return value.strftime("%Y%m%d")


def _combine_date_time(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=UTC)


def _resolve_relative_day(text: str, reference: datetime) -> date | None:
    lowered = text.lower()
    reference_date = reference.astimezone(UTC).date()
    if "übermorgen" in lowered:
        return reference_date + timedelta(days=2)
    if "morgen" in lowered:
        return reference_date + timedelta(days=1)
    if "heute" in lowered:
        return reference_date
    return None


def parse_appointment_window(
    preferred_callback_time: str,
    *,
    reference: datetime,
) -> CalendarEventWindow | None:
    text = preferred_callback_time.strip()
    if not text:
        return None

    lowered = text.lower()
    day = _resolve_relative_day(lowered, reference)

    time_match = _TIME_PATTERN.search(text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        event_day = day or reference.astimezone(UTC).date()
        start = _combine_date_time(event_day, hour, minute)
        return CalendarEventWindow(all_day=False, start=start, end=start + timedelta(hours=1))

    if day is not None:
        if "vormittag" in lowered or "früh" in lowered:
            start = _combine_date_time(day, 9)
            end = _combine_date_time(day, 12)
            return CalendarEventWindow(all_day=False, start=start, end=end)
        if "nachmittag" in lowered or "abend" in lowered:
            start = _combine_date_time(day, 13)
            end = _combine_date_time(day, 17)
            return CalendarEventWindow(all_day=False, start=start, end=end)
        start = _combine_date_time(day, 0)
        end = start + timedelta(days=1)
        return CalendarEventWindow(all_day=True, start=start, end=end)

    return None


def build_lead_calendar_description(
    *,
    company: Company,
    lead: Lead,
    frontend_base_url: str | None = None,
) -> str:
    lines = [
        f"Kontakt: {lead.name or '—'}",
        f"Telefon: {lead.phone or '—'}",
    ]
    if lead.email:
        lines.append(f"E-Mail: {lead.email}")
    lines.append(f"Service: {lead.service_requested or '—'}")
    lines.append(f"Terminwunsch: {lead.preferred_callback_time or '—'}")
    if lead.description:
        lines.append(f"Anliegen: {lead.description}")
    if frontend_base_url:
        dashboard_url = f"{frontend_base_url.rstrip('/')}/leads/{lead.id}"
        lines.append(f"Dashboard: {dashboard_url}")
    lines.append(f"Unternehmen: {company.name}")
    return "\n".join(lines)


def build_lead_calendar_summary(*, company: Company, lead: Lead) -> str:
    summary = lead.summary or lead.service_requested or "Terminanfrage"
    return f"{company.name}: {summary}"


def build_lead_calendar_ics(
    *,
    company: Company,
    lead: Lead,
    frontend_base_url: str | None = None,
) -> str:
    now = datetime.now(UTC)
    window = parse_appointment_window(
        lead.preferred_callback_time,
        reference=lead.created_at or now,
    )
    if window is None:
        event_day = (lead.created_at or now).astimezone(UTC).date()
        window = CalendarEventWindow(
            all_day=True,
            start=_combine_date_time(event_day, 0),
            end=_combine_date_time(event_day, 0) + timedelta(days=1),
        )

    uid = f"lead-{lead.id}@{company.slug or company.id}"
    description = build_lead_calendar_description(
        company=company,
        lead=lead,
        frontend_base_url=frontend_base_url,
    )
    summary = build_lead_calendar_summary(company=company, lead=lead)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AI Anfragen-Assistent//DE",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{_format_ics_timestamp(now)}",
    ]

    if window.all_day:
        start_date = window.start.date()
        end_date = window.end.date()
        lines.append(f"DTSTART;VALUE=DATE:{_format_ics_date(start_date)}")
        lines.append(f"DTEND;VALUE=DATE:{_format_ics_date(end_date)}")
    else:
        lines.append(f"DTSTART:{_format_ics_timestamp(window.start)}")
        lines.append(f"DTEND:{_format_ics_timestamp(window.end)}")

    lines.extend(
        [
            f"SUMMARY:{_escape_ics_text(summary)}",
            f"DESCRIPTION:{_escape_ics_text(description)}",
            "END:VEVENT",
            "END:VCALENDAR",
        ],
    )
    return "\r\n".join(lines) + "\r\n"
