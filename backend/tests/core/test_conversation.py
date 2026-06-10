import pytest

from app.core.memory.models import MessageRole


@pytest.mark.asyncio
async def test_conversation_service_records_and_builds_messages(
    conversation_service,
) -> None:
    conversation_id = "conv-1"
    await conversation_service.record_user_message(conversation_id, "Hello")
    await conversation_service.record_assistant_message(conversation_id, "Hi there")

    history = await conversation_service.get_history(conversation_id)
    messages = await conversation_service.build_messages(
        conversation_id,
        system_prompt="System",
    )

    assert len(history) == 2
    assert history[0].role == MessageRole.USER
    assert history[1].role == MessageRole.ASSISTANT
    assert messages[0].content == "System"
    assert messages[-1].content == "Hi there"
