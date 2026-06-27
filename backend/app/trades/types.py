from enum import StrEnum


class TradeId(StrEnum):
    SKH = "skh"


VALID_TRADE_IDS = frozenset({TradeId.SKH.value})
