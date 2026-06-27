"""Urgency tier helpers for inbox sorting (high → medium → low)."""

from __future__ import annotations

from sqlalchemy import ColumnElement, case, func
from sqlalchemy.orm import InstrumentedAttribute

from app.agents.lead_agent.models import LeadExtractedData

URGENCY_HIGH = frozenset({"high", "hoch", "dringend", "urgent"})
URGENCY_MEDIUM = frozenset({"medium", "mittel"})
URGENCY_LOW = frozenset({"low", "niedrig"})
CANONICAL_URGENCY_LEVELS = frozenset({"hoch", "mittel", "niedrig"})

NOTIFICATION_MIN_URGENCY_LEVELS = frozenset({"high", "medium", "low"})
NOTIFICATION_MIN_URGENCY_RANK = {"high": 3, "medium": 2, "low": 1}

_URGENCY_HIGH_PHRASES = (
    "heute",
    "sofort",
    "notfall",
    "notfäll",
    "dringend",
    "asap",
    "eilig",
    "schnellstmöglich",
    "schnell",
    "jetzt",
    "urgent",
    "today",
    "emergency",
    "noch heute",
)
_URGENCY_MEDIUM_PHRASES = (
    "morgen",
    "diese woche",
    "bald",
    "zeitnah",
    "tomorrow",
    "in den nächsten tagen",
    "nächste tage",
)
_URGENCY_LOW_PHRASES = (
    "keine eile",
    "nicht dringend",
    "flexibel",
    "nächste woche",
    "irgendwann",
    "später",
    "low priority",
    "whenever",
)


def _contains_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def resolve_urgency_level(value: str | None) -> str | None:
    """Map free-text or tier labels to canonical German urgency: hoch, mittel, niedrig."""
    normalized = (value or "").strip().lower()
    if not normalized:
        return None
    if normalized in URGENCY_HIGH:
        return "hoch"
    if normalized in URGENCY_MEDIUM:
        return "mittel"
    if normalized in URGENCY_LOW:
        return "niedrig"
    if _contains_phrase(normalized, _URGENCY_HIGH_PHRASES):
        return "hoch"
    if _contains_phrase(normalized, _URGENCY_MEDIUM_PHRASES):
        return "mittel"
    if _contains_phrase(normalized, _URGENCY_LOW_PHRASES):
        return "niedrig"
    return None


def sanitize_urgency_fields(data: LeadExtractedData) -> LeadExtractedData:
    """Normalize urgency tiers and preserve timing phrases as callback preference."""
    updates: dict[str, str] = {}

    if data.urgency:
        resolved = resolve_urgency_level(data.urgency)
        if resolved:
            updates["urgency"] = resolved
            raw = data.urgency.strip()
            if (
                raw.lower() not in CANONICAL_URGENCY_LEVELS
                and not data.preferred_callback_time
                and resolve_urgency_level(raw) is not None
            ):
                updates["preferred_callback_time"] = raw

    if "urgency" not in updates and data.preferred_callback_time:
        resolved = resolve_urgency_level(data.preferred_callback_time)
        if resolved:
            updates["urgency"] = resolved

    if not updates:
        return data
    return data.model_copy(update=updates)


def urgency_sort_rank(value: str | None) -> int:
    resolved = resolve_urgency_level(value)
    if resolved == "hoch":
        return 3
    if resolved == "mittel":
        return 2
    if resolved == "niedrig":
        return 1
    normalized = (value or "").strip().lower()
    if normalized in URGENCY_HIGH:
        return 3
    if normalized in URGENCY_MEDIUM:
        return 2
    if normalized in URGENCY_LOW:
        return 1
    return 0


def meets_notification_min_urgency(
    lead_urgency: str | None,
    min_level: str,
) -> bool:
    lead_rank = urgency_sort_rank(lead_urgency)
    if lead_rank == 0:
        return False
    min_rank = NOTIFICATION_MIN_URGENCY_RANK.get(min_level, 2)
    return lead_rank >= min_rank


def urgency_sort_rank_expression(column: InstrumentedAttribute[str]) -> ColumnElement[int]:
    normalized = func.lower(func.trim(column))
    return case(
        (normalized.in_(URGENCY_HIGH), 3),
        (normalized.in_(URGENCY_MEDIUM), 2),
        (normalized.in_(URGENCY_LOW), 1),
        else_=0,
    )
