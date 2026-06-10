from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.conversation import Conversation
from app.db.models.enums import ConversationChannel, MessageRole
from app.db.models.message import Message


class ConversationRepository:
    """Persistence layer for tenant conversations and messages."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        company_id: UUID,
        external_id: str,
        channel: ConversationChannel = ConversationChannel.WEB,
    ) -> Conversation:
        conversation = Conversation(
            company_id=company_id,
            external_id=external_id,
            channel=channel.value,
        )
        self._session.add(conversation)
        self._session.commit()
        self._session.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: UUID, *, company_id: UUID | None = None) -> Conversation | None:
        conversation = self._session.get(Conversation, conversation_id)
        if conversation is None:
            return None
        if company_id is not None and conversation.company_id != company_id:
            return None
        return conversation

    def get_by_external_id(
        self,
        *,
        company_id: UUID,
        external_id: str,
    ) -> Conversation | None:
        return (
            self._session.query(Conversation)
            .filter(
                Conversation.company_id == company_id,
                Conversation.external_id == external_id,
            )
            .one_or_none()
        )

    def get_or_create_by_external_id(
        self,
        *,
        company_id: UUID,
        external_id: str,
        channel: ConversationChannel,
    ) -> Conversation:
        existing = self.get_by_external_id(company_id=company_id, external_id=external_id)
        if existing is not None:
            return existing
        return self.create(company_id=company_id, external_id=external_id, channel=channel)

    def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role.value,
            content=content,
            message_metadata=metadata,
        )
        conversation = self._session.get(Conversation, conversation_id)
        if conversation is not None:
            conversation.updated_at = datetime.now(UTC)

        self._session.add(message)
        self._session.commit()
        self._session.refresh(message)
        return message

    def list_messages(self, conversation_id: UUID) -> list[Message]:
        return (
            self._session.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )
