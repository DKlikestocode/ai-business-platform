from app.agents.lead_agent.models import LeadExtractedData
from app.agents.lead_agent.urgency import (
    meets_notification_min_urgency,
    resolve_urgency_level,
    sanitize_urgency_fields,
    urgency_sort_rank,
)


def test_resolve_urgency_level_maps_canonical_labels() -> None:
    assert resolve_urgency_level("hoch") == "hoch"
    assert resolve_urgency_level("high") == "hoch"
    assert resolve_urgency_level("mittel") == "mittel"
    assert resolve_urgency_level("medium") == "mittel"
    assert resolve_urgency_level("niedrig") == "niedrig"
    assert resolve_urgency_level("low") == "niedrig"


def test_resolve_urgency_level_maps_timing_phrases() -> None:
    assert resolve_urgency_level("heute") == "hoch"
    assert resolve_urgency_level("heute oder morgen") == "hoch"
    assert resolve_urgency_level("morgen") == "mittel"
    assert resolve_urgency_level("keine Eile") == "niedrig"
    assert resolve_urgency_level("unbekannt") is None


def test_sanitize_urgency_fields_preserves_callback_wording() -> None:
    data = LeadExtractedData(urgency="heute oder morgen")

    cleaned = sanitize_urgency_fields(data)

    assert cleaned.urgency == "hoch"
    assert cleaned.preferred_callback_time == "heute oder morgen"


def test_sanitize_urgency_fields_infers_from_callback_time() -> None:
    data = LeadExtractedData(preferred_callback_time="morgen früh")

    cleaned = sanitize_urgency_fields(data)

    assert cleaned.urgency == "mittel"


def test_urgency_sort_rank_orders_high_medium_low() -> None:
    assert urgency_sort_rank("hoch") > urgency_sort_rank("mittel")
    assert urgency_sort_rank("mittel") > urgency_sort_rank("niedrig")
    assert urgency_sort_rank("high") == urgency_sort_rank("hoch")
    assert urgency_sort_rank("medium") == urgency_sort_rank("mittel")
    assert urgency_sort_rank("low") == urgency_sort_rank("niedrig")
    assert urgency_sort_rank(None) == 0
    assert urgency_sort_rank("heute") == urgency_sort_rank("hoch")
    assert urgency_sort_rank("unbekannt") == 0


def test_meets_notification_min_urgency() -> None:
    assert meets_notification_min_urgency("hoch", "medium") is True
    assert meets_notification_min_urgency("mittel", "medium") is True
    assert meets_notification_min_urgency("niedrig", "medium") is False
    assert meets_notification_min_urgency("hoch", "high") is True
    assert meets_notification_min_urgency("mittel", "high") is False
    assert meets_notification_min_urgency("niedrig", "low") is True
    assert meets_notification_min_urgency(None, "low") is False
