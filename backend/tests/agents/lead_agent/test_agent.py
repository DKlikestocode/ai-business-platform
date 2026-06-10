import pytest

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.core.agent_engine.context import AgentContext


@pytest.mark.asyncio
async def test_lead_capture_agent_name_and_prompt() -> None:
    agent = LeadCaptureAgent()

    assert agent.name == "lead-capture-agent"
    assert "qualifies inbound customer inquiries" in agent.description.lower()

    prompt = await agent.build_system_prompt(
        AgentContext(conversation_id="conv-1", agent_name=agent.name),
    )
    assert "kundenanfragen" in prompt.lower()
    assert "sie-form" in prompt.lower()


@pytest.mark.asyncio
async def test_lead_capture_agent_includes_known_data_in_prompt() -> None:
    agent = LeadCaptureAgent()
    prompt = await agent.build_system_prompt(
        AgentContext(
            conversation_id="conv-1",
            agent_name=agent.name,
            metadata={"known_lead_data": {"name": "Jane"}},
        ),
    )

    assert "Known lead data collected so far" in prompt
    assert "Jane" in prompt
