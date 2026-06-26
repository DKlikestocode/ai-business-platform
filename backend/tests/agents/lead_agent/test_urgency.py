from app.agents.lead_agent.urgency import urgency_sort_rank


def test_urgency_sort_rank_orders_high_medium_low() -> None:
    assert urgency_sort_rank("hoch") > urgency_sort_rank("mittel")
    assert urgency_sort_rank("mittel") > urgency_sort_rank("niedrig")
    assert urgency_sort_rank("high") == urgency_sort_rank("hoch")
    assert urgency_sort_rank("medium") == urgency_sort_rank("mittel")
    assert urgency_sort_rank("low") == urgency_sort_rank("niedrig")
    assert urgency_sort_rank(None) == 0
    assert urgency_sort_rank("unbekannt") == 0
