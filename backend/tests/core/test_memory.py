import pytest

from app.core.memory.models import MessageRole


@pytest.mark.asyncio
async def test_in_memory_store_messages_and_context(memory_store) -> None:
    from app.core.memory.models import ConversationMessage

    conversation_id = "conv-1"
    await memory_store.append_message(
        conversation_id,
        ConversationMessage(role=MessageRole.USER, content="Hi"),
    )
    await memory_store.update_context(conversation_id, {"lead_id": "123"})

    messages = await memory_store.get_messages(conversation_id)
    context = await memory_store.get_context(conversation_id)

    assert len(messages) == 1
    assert messages[0].content == "Hi"
    assert context.data["lead_id"] == "123"

    await memory_store.clear_conversation(conversation_id)
    assert await memory_store.get_messages(conversation_id) == []
