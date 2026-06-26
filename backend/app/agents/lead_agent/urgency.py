"""Urgency tier helpers for inbox sorting (high → medium → low)."""

from __future__ import annotations

from sqlalchemy import ColumnElement, case, func
from sqlalchemy.orm import InstrumentedAttribute

URGENCY_HIGH = frozenset({"high", "hoch", "dringend", "urgent"})
URGENCY_MEDIUM = frozenset({"medium", "mittel"})
URGENCY_LOW = frozenset({"low", "niedrig"})


def urgency_sort_rank(value: str | None) -> int:
    normalized = (value or "").strip().lower()
    if normalized in URGENCY_HIGH:
        return 3
    if normalized in URGENCY_MEDIUM:
        return 2
    if normalized in URGENCY_LOW:
        return 1
    return 0


def urgency_sort_rank_expression(column: InstrumentedAttribute[str]) -> ColumnElement[int]:
    normalized = func.lower(func.trim(column))
    return case(
        (normalized.in_(URGENCY_HIGH), 3),
        (normalized.in_(URGENCY_MEDIUM), 2),
        (normalized.in_(URGENCY_LOW), 1),
        else_=0,
    )
