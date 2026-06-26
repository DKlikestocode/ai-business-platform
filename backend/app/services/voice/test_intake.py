from uuid import uuid4

from app.agents.lead_agent.models import LeadMessageRequest

TEST_VOICE_CALLER_PHONE = "+491701234567"
TEST_VOICE_INTAKE_MESSAGE = (
    "Wir haben einen Wasserrohrbruch in der Küche in München, PLZ 80331. "
    "Es ist dringend. Mein Name ist Max Test. Rückruf bitte heute Nachmittag."
)


def build_dashboard_test_voice_request() -> LeadMessageRequest:
    return LeadMessageRequest(
        conversation_id=f"dashboard-test-voice-{uuid4().hex[:12]}",
        message=TEST_VOICE_INTAKE_MESSAGE,
    )
