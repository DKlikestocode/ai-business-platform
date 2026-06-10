from app.demo.data import DEMO_LEAD_SEEDS


def test_demo_leads_cover_german_small_business_scenarios() -> None:
    services = {seed.data.service_requested for seed in DEMO_LEAD_SEEDS}
    locations = {seed.data.location for seed in DEMO_LEAD_SEEDS}

    assert "Dachreparatur nach Sturm" in services
    assert "Elektroinstallation Smart Home" in services
    assert "Sanitär-Notdienst" in services
    assert "Immobilienbewertung" in services
    assert "Firmenfitness-Angebot" in services
    assert any("München" in location for location in locations)
    assert any("Berlin" in location for location in locations)
    assert any("Hamburg" in location for location in locations)
    assert any("Köln" in location for location in locations)
