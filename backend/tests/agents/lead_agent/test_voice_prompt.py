import pytest

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.agents.lead_agent.voice_prompt import VOICE_CHANNEL_PROMPT
from app.core.agent_engine.context import AgentContext


@pytest.mark.asyncio
async def test_voice_channel_prompt_appended_when_flag_set() -> None:
    agent = LeadCaptureAgent()
    prompt = await agent.build_system_prompt(
        AgentContext(
            conversation_id="voice-1",
            agent_name=agent.name,
            metadata={"channel_voice_prompt": True},
        ),
    )
    assert VOICE_CHANNEL_PROMPT.strip() in prompt


@pytest.mark.asyncio
async def test_voice_channel_prompt_omitted_for_web() -> None:
    agent = LeadCaptureAgent()
    prompt = await agent.build_system_prompt(
        AgentContext(
            conversation_id="web-1",
            agent_name=agent.name,
            metadata={},
        ),
    )
    assert "Telefon-Kanal" not in prompt
