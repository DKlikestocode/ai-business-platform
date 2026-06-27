from app.trades.packs.skh import SKH_AGENT_PROMPT
from app.trades.types import TradeId, VALID_TRADE_IDS

_TRADE_PROMPTS: dict[str, str] = {
    TradeId.SKH.value: SKH_AGENT_PROMPT,
}


def is_valid_trade(value: str | None) -> bool:
    if value is None:
        return True
    return value in VALID_TRADE_IDS


def build_trade_prompt(trade: str | None) -> str | None:
    if not trade:
        return None
    return _TRADE_PROMPTS.get(trade)
