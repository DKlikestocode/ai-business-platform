"""Helpers for trade-specific inquiry scope classification."""

from typing import Literal

InquiryScope = Literal["in_scope", "out_of_scope", "unclear"]


def is_trade_configured(trade: str | None) -> bool:
    return bool(trade and trade.strip())


def is_inquiry_out_of_scope(
    inquiry_scope: InquiryScope | None,
    *,
    trade: str | None,
) -> bool:
    return is_trade_configured(trade) and inquiry_scope == "out_of_scope"
