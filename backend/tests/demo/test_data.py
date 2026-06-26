from app.demo.data import DEMO_LEAD_SEEDS


def test_demo_leads_cover_german_small_business_scenarios() -> None:
    services = {seed.data.service_requested for seed in DEMO_LEAD_SEEDS}
    locations = {seed.data.location for seed in DEMO_LEAD_SEEDS}
    postal_codes = {seed.data.postal_code for seed in DEMO_LEAD_SEEDS}

    assert "Dachreparatur nach Sturm" in services
    assert "Elektroinstallation Smart Home" in services
    assert "Sanitär-Notdienst" in services
    assert "Immobilienbewertung" in services
    assert "Firmenfitness-Angebot" in services
    assert any("Hamburg" in location for location in locations)
    assert any("Bremen" in location for location in locations)
    assert all(postal_code and len(postal_code) == 5 for postal_code in postal_codes)
