from app.agents.lead_agent.voice_prompt import VOICE_CHANNEL_PROMPT
from app.core.agent_engine.base import BaseAgent
from app.core.agent_engine.context import AgentContext

LEAD_CAPTURE_SYSTEM_PROMPT = """Sie sind der Lead-Capture-Agent für eine kleine Unternehmensplattform.

Ihr Ziel ist es, eingehende Kundenanfragen freundlich und professionell zu qualifizieren.

Erfassen Sie folgende Informationen:
- Erforderlich für die vollständige Qualifizierung: name, phone, postal_code, location, service_requested, description, urgency, preferred_callback_time
- Optional: email, company

Richtlinien:
- Antworten Sie immer auf Deutsch in der Sie-Form.
- Stellen Sie jeweils nur eine oder zwei gezielte Fragen.
- Wenn weder Telefon noch E-Mail bekannt ist, fragen Sie zuerst nach einer Kontaktmöglichkeit.
- Akzeptieren Sie nur gut lesbare Telefonnummern (z. B. 0170 1234567, +49 170 1234567) und gültige E-Mail-Adressen (z. B. name@beispiel.de).
- Wenn eine Kontaktmöglichkeit vorhanden ist, die Beschreibung aber unzureichend ist, fragen Sie nach dem Problem oder dem gewünschten Service.
- Wenn der Lead mit hilfreichem Kontext kontaktierbar ist, bestätigen Sie den Eingang der Anfrage.
- Bestätigen Sie Angaben, wenn der Kunde sie mitteilt.
- Halten Sie Antworten kurz und hilfreich.
- Erfinden Sie keine Informationen, die der Kunde nicht genannt hat.
- Wiederholen Sie keine unnötigen Fragen.
- Wenn alle erforderlichen Felder erfasst sind, bestätigen Sie die nächsten Schritte und den voraussichtlichen Rückruf.
- Geben Sie keine Preise oder Kostenzusagen.
- Garantieren Sie keine festen Termine oder verbindlichen Rückrufzeiten.
"""


class LeadCaptureAgent(BaseAgent):
    """Agent that qualifies inbound customer inquiries for small businesses."""

    AGENT_NAME = "lead-capture-agent"

    def __init__(self) -> None:
        super().__init__(
            name=self.AGENT_NAME,
            description="Qualifies inbound customer inquiries and captures lead details.",
            tool_names=[],
            system_prompt=LEAD_CAPTURE_SYSTEM_PROMPT,
        )

    async def build_system_prompt(self, context: AgentContext) -> str:
        prompt = await super().build_system_prompt(context)
        sections = [prompt]

        known_data = context.metadata.get("known_lead_data")
        if known_data:
            sections.append(
                "Known lead data collected so far:\n"
                f"{known_data}\n"
                "Use this context to avoid re-asking for confirmed details."
            )

        qualification_hint = context.metadata.get("qualification_hint")
        if qualification_hint:
            sections.append(f"Current qualification guidance:\n{qualification_hint}")

        service_area_prompt = context.metadata.get("service_area_prompt")
        if service_area_prompt:
            sections.append(f"Service area guidance:\n{service_area_prompt}")

        service_area_status_prompt = context.metadata.get("service_area_status_prompt")
        if service_area_status_prompt:
            sections.append(f"Service area check:\n{service_area_status_prompt}")

        if context.metadata.get("channel_voice_prompt"):
            sections.append(VOICE_CHANNEL_PROMPT)

        return "\n\n".join(sections)
