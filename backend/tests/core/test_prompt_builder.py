from app.core.memory.models import ConversationMessage, MessageRole
from app.core.prompts.builder import PromptBuilder


def test_prompt_builder_includes_system_and_history() -> None:
    builder = PromptBuilder()
    history = [
        ConversationMessage(role=MessageRole.USER, content="Hello"),
    ]

    messages = builder.build(system_prompt="System rules", history=history)

    assert messages[0].role == MessageRole.SYSTEM
    assert messages[0].content == "System rules"
    assert messages[1].role == MessageRole.USER
    assert messages[1].content == "Hello"


def test_prompt_builder_can_omit_system_prompt() -> None:
    builder = PromptBuilder()
    messages = builder.build(system_prompt="", history=[], include_system=False)
    assert messages == []
