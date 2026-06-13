from enum import StrEnum

from app.db.models.enums import ConversationChannel


class InquirySource(StrEnum):
    WEBSITE = "website"
    TEST = "test"


def channel_to_inquiry_source(
    channel: ConversationChannel | None,
) -> InquirySource:
    # Leads without a matching conversation row default to Website for legacy data.
    if channel == ConversationChannel.DASHBOARD:
        return InquirySource.TEST
    return InquirySource.WEBSITE
