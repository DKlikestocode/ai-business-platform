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
            phone="+49 89 1234 5678",
            email="thomas.weber@email.de",
            company="Weber Dach GmbH",
            location="München, Bayern",
            service_requested="Dachreparatur nach Sturm",
            description=(
                "Mehrere Dachziegel sind abgedriftet und es tropft leicht "
                "in den Dachboden. Bitte zeitnahe Begutachtung."
            ),
            urgency="hoch",
            preferred_callback_time="Heute Nachmittag ab 15:00 Uhr",
        ),
        summary="Dachdecker-Anfrage wegen Sturmschaden in München.",
        status=LeadStatus.NEW,
    ),
    DemoLeadSeed(
        conversation_id="demo-elektriker-001",
        data=LeadExtractedData(
            name="Sandra Klein",
            phone="+49 30 9876 5432",
            email="s.klein@klein-berlin.de",
            company=None,
            location="Berlin, Prenzlauer Berg",
            service_requested="Elektroinstallation Smart Home",
            description=(
                "Neue Wohnung, ich möchte Rolladen, Licht und Heizung "
                "per App steuern lassen. Angebot für 3-Zimmer-Wohnung."
            ),
            urgency="mittel",
            preferred_callback_time="Donnerstag Vormittag",
        ),
        summary="Elektriker-Anfrage für Smart-Home-Nachrüstung in Berlin.",
        status=LeadStatus.CONTACTED,
    ),
    DemoLeadSeed(
        conversation_id="demo-sanitaer-001",
        data=LeadExtractedData(
            name="Michael Bauer",
            phone="+49 40 5555 7788",
            email=None,
            company="Cafe Hafenblick",
            location="Hamburg, Altona",
            service_requested="Sanitär-Notdienst",
            description=(
                "Undichtes Abwasserrohr in der Gästetoilette des Cafés. "
                "Betrieb muss am Wochenende weiterlaufen."
            ),
            urgency="hoch",
            preferred_callback_time="Morgen früh ab 8:00 Uhr",
        ),
        summary="Sanitär-Notfall für Gastronomiebetrieb in Hamburg.",
        status=LeadStatus.QUALIFIED,
    ),
    DemoLeadSeed(
        conversation_id="demo-immobilienmakler-001",
        data=LeadExtractedData(
            name="Anna Hoffmann",
            phone="+49 221 4444 9900",
            email="anna.hoffmann@immobilien-koeln.de",
            company="Hoffmann Immobilien",
            location="Köln, Lindenthal",
            service_requested="Immobilienbewertung",
            description=(
                "Eigentumswohnung mit 85 m², Baujahr 1998, soll in den "
                "nächsten 8 Wochen verkauft werden. Marktwertgutachten gewünscht."
            ),
            urgency="mittel",
            preferred_callback_time="Freitag zwischen 10:00 und 12:00 Uhr",
        ),
        summary="Makler-Anfrage für Verkaufsbewertung einer Eigentumswohnung in Köln.",
        status=LeadStatus.WON,
    ),
    DemoLeadSeed(
        conversation_id="demo-fitnessstudio-001",
        data=LeadExtractedData(
            name="Julia Richter",
            phone="+49 89 7777 2211",
            email="julia.richter@fitlife-koeln.de",
            company="FitLife Köln GmbH",
            location="Köln, Ehrenfeld",
            service_requested="Firmenfitness-Angebot",
            description=(
                "Wir planen ein Firmenfitness-Programm für 45 Mitarbeitende "
                "und suchen ein Studio mit Corporate Membership und Räumen "
                "für Functional Training."
            ),
            urgency="niedrig",
            preferred_callback_time="Nächste Woche Dienstag Nachmittag",
        ),
        summary="Fitnessstudio-Anfrage für Firmenfitness mit 45 Mitarbeitenden.",
        status=LeadStatus.LOST,
    ),
)

DEMO_CONVERSATION_IDS: frozenset[str] = frozenset(
    seed.conversation_id for seed in DEMO_LEAD_SEEDS
)
