from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models.conversation import Conversation
from app.db.models.enums import ConversationChannel, MessageRole
from app.db.models.message import Message


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationMessagesResponse(BaseModel):
    conversation_id: UUID
    external_id: str
    channel: ConversationChannel
    messages: list[MessageResponse] = Field(default_factory=list)


def message_to_response(message: Message) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=MessageRole(message.role),
        content=message.content,
        metadata=message.message_metadata,
        created_at=message.created_at,
    )


def build_conversation_messages_response(
    conversation: Conversation,
    messages: list[Message],
) -> ConversationMessagesResponse:
    return ConversationMessagesResponse(
        conversation_id=conversation.id,
        external_id=conversation.external_id,
        channel=ConversationChannel(conversation.channel),
        messages=[message_to_response(message) for message in messages],
    )
