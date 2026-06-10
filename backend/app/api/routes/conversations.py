from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_conversation_repository, get_current_tenant_id, get_current_user
from app.api.schemas.conversations import ConversationMessagesResponse, build_conversation_messages_response
from app.db.models.user import User
from app.repositories.conversation_repository import ConversationRepository

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get(
    "/{conversation_id}/messages",
    response_model=ConversationMessagesResponse,
    summary="List messages for a conversation",
)
def list_conversation_messages(
    conversation_id: str,
    company_id: UUID = Depends(get_current_tenant_id),
    repository: ConversationRepository = Depends(get_conversation_repository),
    _: User = Depends(get_current_user),
) -> ConversationMessagesResponse:
    conversation = repository.get_by_external_id(
        company_id=company_id,
        external_id=conversation_id,
    )
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found.",
        )

    messages = repository.list_messages(conversation.id)
    return build_conversation_messages_response(conversation, messages)
