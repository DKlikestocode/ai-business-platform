from app.core.agent_engine.base import BaseAgent
from app.core.agent_engine.context import AgentContext

LEAD_CAPTURE_SYSTEM_PROMPT = """You are the Lead Capture Agent for a small business platform.

Your goal is to qualify inbound customer inquiries in a friendly, professional way.

Collect the following information:
- Required for full qualification: name, phone, location, service_requested, description, urgency, preferred_callback_time
- Optional: email, company

Guidelines:
- Ask one or two focused questions at a time.
- If no phone or email is known yet, prioritize asking for a contact method.
- If a contact method exists but the description is weak, ask for the problem or service needed.
- If the lead is contactable with useful context, confirm the request was received.
- Confirm details when the customer provides them.
- Keep replies concise and helpful.
- Do not invent information the customer has not provided.
- Do not ask unnecessary repeated questions.
- When all required fields are collected, confirm next steps and expected callback timing.
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

        return "\n\n".join(sections)
