from app.services.notifications.lead_email_template import build_owner_lead_notification


def test_owner_lead_notification_plain_text_excludes_internal_fields() -> None:
    class _Company:
        name = "Muster GmbH"

    class _Lead:
        id = "00000000-0000-0000-0000-000000000001"
        summary = "Rohrbruch in Hamburg"
        name = "Max Mustermann"
        phone = "01701234567"
        email = "max@example.com"
        location = "Hamburg"
        service_requested = "Sanitär"
        urgency = "high"
        preferred_callback_time = "morgen ab 10 Uhr"
        description = "Wasserschaden in der Küche"

    plain, html = build_owner_lead_notification(
        company=_Company(),
        lead=_Lead(),
        frontend_base_url="https://app.example.com",
    )

    assert "Rohrbruch in Hamburg" in plain
    assert "Name: Max Mustermann" in plain
    assert "Qualifizierungsstatus" not in plain
    assert "Kontaktmethode" not in plain
    assert "Anfrage im Dashboard öffnen:" in plain
    assert "Neue Anfrage" in html
    assert "Anfrage im Dashboard öffnen" in html
    assert "Qualifizierungsstatus" not in html
