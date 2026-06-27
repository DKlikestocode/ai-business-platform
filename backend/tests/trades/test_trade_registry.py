import pytest

from app.agents.lead_agent.agent import LeadCaptureAgent
from app.core.agent_engine.context import AgentContext
from app.trades.registry import build_trade_prompt, is_valid_trade
from app.trades.types import TradeId


def test_is_valid_trade() -> None:
    assert is_valid_trade(None) is True
    assert is_valid_trade(TradeId.SKH.value) is True
    assert is_valid_trade("invalid") is False


def test_build_trade_prompt_for_skh() -> None:
    prompt = build_trade_prompt(TradeId.SKH.value)

    assert prompt is not None
    assert "Sanitär" in prompt
    assert "Heizung" in prompt


@pytest.mark.asyncio
async def test_agent_includes_trade_prompt_in_system_prompt() -> None:
    agent = LeadCaptureAgent()
    trade_prompt = build_trade_prompt(TradeId.SKH.value)
    context = AgentContext(
        conversation_id="conv-trade",
        agent_name=agent.name,
        metadata={"trade_prompt": trade_prompt},
    )

    prompt = await agent.build_system_prompt(context)

    assert "Branchen-Kontext" in prompt
    assert "Sanitär" in prompt
