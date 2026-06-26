from app.agents.lead_agent.inquiry_source import InquirySource, channel_to_inquiry_source
from app.db.models.enums import ConversationChannel


def test_dashboard_channel_maps_to_test_source() -> None:
    assert channel_to_inquiry_source(ConversationChannel.DASHBOARD) == InquirySource.TEST


def test_web_channel_maps_to_website_source() -> None:
    assert channel_to_inquiry_source(ConversationChannel.WEB) == InquirySource.WEBSITE


def test_missing_channel_defaults_to_website_source() -> None:
    assert channel_to_inquiry_source(None) == InquirySource.WEBSITE


def test_landing_demo_channel_maps_to_test_source() -> None:
    assert channel_to_inquiry_source(ConversationChannel.LANDING_DEMO) == InquirySource.TEST


def test_voice_channel_maps_to_phone_source() -> None:
    assert channel_to_inquiry_source(ConversationChannel.VOICE) == InquirySource.PHONE
