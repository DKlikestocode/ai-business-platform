from app.agents.lead_agent.inquiry_scope import (
    is_inquiry_out_of_scope,
    is_trade_configured,
)


def test_is_trade_configured() -> None:
    assert is_trade_configured("skh") is True
    assert is_trade_configured(None) is False
    assert is_trade_configured("") is False


def test_is_inquiry_out_of_scope_requires_trade_and_scope() -> None:
    assert is_inquiry_out_of_scope("out_of_scope", trade="skh") is True
    assert is_inquiry_out_of_scope("in_scope", trade="skh") is False
    assert is_inquiry_out_of_scope("unclear", trade="skh") is False
    assert is_inquiry_out_of_scope("out_of_scope", trade=None) is False
