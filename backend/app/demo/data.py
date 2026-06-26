from dataclasses import dataclass

from app.agents.lead_agent.models import LeadExtractedData, LeadStatus


@dataclass(frozen=True)
class DemoLeadSeed:
    conversation_id: str
    data: LeadExtractedData
    summary: str
    status: LeadStatus


DEMO_LEAD_SEEDS: tuple[DemoLeadSeed, ...] = (
    DemoLeadSeed(
        conversation_id="demo-dachdecker-001",
        data=LeadExtractedData(
            name="Thomas Weber",
            phone="+49 40 3012345",
            email="thomas.weber@email.de",
            company="Weber Dach GmbH",
            location="Hamburg, Barmbek",
            postal_code="22303",
            service_requested="Dachreparatur nach Sturm",
            description=(
                "Mehrere Dachziegel sind abgedriftet und es tropft leicht "
                "in den Dachboden. Bitte zeitnahe Begutachtung."
            ),
            urgency="hoch",
            preferred_callback_time="Heute Nachmittag ab 15:00 Uhr",
        ),
        summary="Dachdecker-Anfrage wegen Sturmschaden in Hamburg-Barmbek.",
        status=LeadStatus.NEW,
    ),
    DemoLeadSeed(
        conversation_id="demo-elektriker-001",
        data=LeadExtractedData(
            name="Sandra Klein",
            phone="+49 40 9876543",
            email="s.klein@example.de",
            company=None,
            location="Hamburg, Bergedorf",
            postal_code="21029",
            service_requested="Elektroinstallation Smart Home",
            description=(
                "Neue Wohnung, ich möchte Rolladen, Licht und Heizung "
                "per App steuern lassen. Angebot für 3-Zimmer-Wohnung."
            ),
            urgency="mittel",
            preferred_callback_time="Donnerstag Vormittag",
        ),
        summary="Elektriker-Anfrage für Smart-Home-Nachrüstung in Hamburg.",
        status=LeadStatus.NEW,
    ),
    DemoLeadSeed(
        conversation_id="demo-sanitaer-001",
        data=LeadExtractedData(
            name="Michael Bauer",
            phone="+49 40 55557788",
            email=None,
            company="Café Hafenblick",
            location="Hamburg, Altona",
            postal_code="22765",
            service_requested="Sanitär-Notdienst",
            description=(
                "Undichtes Abwasserrohr in der Gästetoilette des Cafés. "
                "Betrieb muss am Wochenende weiterlaufen."
            ),
            urgency="hoch",
            preferred_callback_time="Morgen früh ab 8:00 Uhr",
        ),
        summary="Sanitär-Notfall für Gastronomiebetrieb in Hamburg-Altona.",
        status=LeadStatus.NEW,
    ),
    DemoLeadSeed(
        conversation_id="demo-immobilienmakler-001",
        data=LeadExtractedData(
            name="Anna Hoffmann",
            phone="+49 421 4444990",
            email="anna.hoffmann@immobilien-bremen.de",
            company="Hoffmann Immobilien",
            location="Bremen, Neustadt",
            postal_code="28195",
            service_requested="Immobilienbewertung",
            description=(
                "Eigentumswohnung mit 85 m², Baujahr 1998, soll in den "
                "nächsten 8 Wochen verkauft werden. Marktwertgutachten gewünscht."
            ),
            urgency="mittel",
            preferred_callback_time="Freitag zwischen 10:00 und 12:00 Uhr",
        ),
        summary="Makler-Anfrage für Verkaufsbewertung in Bremen.",
        status=LeadStatus.NEW,
    ),
    DemoLeadSeed(
        conversation_id="demo-fitnessstudio-001",
        data=LeadExtractedData(
            name="Julia Richter",
            phone="+49 471 7777221",
            email="julia.richter@fitlife-bremerhaven.de",
            company="FitLife Bremerhaven GmbH",
            location="Bremerhaven",
            postal_code="27568",
            service_requested="Firmenfitness-Angebot",
            description=(
                "Wir planen ein Firmenfitness-Programm für 45 Mitarbeitende "
                "und suchen ein Studio mit Corporate Membership und Räumen "
                "für Functional Training."
            ),
            urgency="niedrig",
            preferred_callback_time="Nächste Woche Dienstag Nachmittag",
        ),
        summary="Fitnessstudio-Anfrage für Firmenfitness in Bremerhaven.",
        status=LeadStatus.NEW,
    ),
)

DEMO_CONVERSATION_IDS: frozenset[str] = frozenset(
    seed.conversation_id for seed in DEMO_LEAD_SEEDS
)
