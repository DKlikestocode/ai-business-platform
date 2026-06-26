from app.agents.lead_agent.urgency import meets_notification_min_urgency, urgency_sort_rank


def test_urgency_sort_rank_orders_high_medium_low() -> None:
    assert urgency_sort_rank("hoch") > urgency_sort_rank("mittel")
    assert urgency_sort_rank("mittel") > urgency_sort_rank("niedrig")
    assert urgency_sort_rank("high") == urgency_sort_rank("hoch")
    assert urgency_sort_rank("medium") == urgency_sort_rank("mittel")
    assert urgency_sort_rank("low") == urgency_sort_rank("niedrig")
    assert urgency_sort_rank(None) == 0
    assert urgency_sort_rank("unbekannt") == 0


def test_meets_notification_min_urgency() -> None:
    assert meets_notification_min_urgency("hoch", "medium") is True
    assert meets_notification_min_urgency("mittel", "medium") is True
    assert meets_notification_min_urgency("niedrig", "medium") is False
    assert meets_notification_min_urgency("hoch", "high") is True
    assert meets_notification_min_urgency("mittel", "high") is False
    assert meets_notification_min_urgency("niedrig", "low") is True
    assert meets_notification_min_urgency(None, "low") is False
