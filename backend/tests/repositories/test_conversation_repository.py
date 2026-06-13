from uuid import uuid4

from app.db.models.company import Company
from app.db.models.enums import ConversationChannel, MessageRole
from app.repositories.conversation_repository import ConversationRepository


def test_get_or_create_by_external_id_is_idempotent(
    conversation_repository: ConversationRepository,
    company: Company,
) -> None:
    first = conversation_repository.get_or_create_by_external_id(
        company_id=company.id,
        external_id="conv-abc",
        channel=ConversationChannel.WEB,
    )
    second = conversation_repository.get_or_create_by_external_id(
        company_id=company.id,
        external_id="conv-abc",
        channel=ConversationChannel.WEB,
    )

    assert first.id == second.id
    assert first.external_id == "conv-abc"
    assert first.channel == ConversationChannel.WEB.value


def test_add_message_and_list_messages(
    conversation_repository: ConversationRepository,
    company: Company,
) -> None:
    conversation = conversation_repository.get_or_create_by_external_id(
        company_id=company.id,
        external_id="conv-messages",
        channel=ConversationChannel.WEB,
    )

    conversation_repository.add_message(
        conversation.id,
        MessageRole.USER,
        "Hello",
        metadata={"source": "test"},
    )
    conversation_repository.add_message(
        conversation.id,
        MessageRole.ASSISTANT,
        "Hi there",
        metadata={"lead_data": {"name": "Jane"}},
    )

    messages = conversation_repository.list_messages(conversation.id)

    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER.value
    assert messages[0].content == "Hello"
    assert messages[0].message_metadata == {"source": "test"}
    assert messages[1].role == MessageRole.ASSISTANT.value
    assert messages[1].message_metadata == {"lead_data": {"name": "Jane"}}


def test_get_or_create_upgrades_web_channel_to_dashboard(
    conversation_repository: ConversationRepository,
    company: Company,
) -> None:
    existing = conversation_repository.create(
        company_id=company.id,
        external_id="demo-chat-001",
        channel=ConversationChannel.WEB,
    )

    upgraded = conversation_repository.get_or_create_by_external_id(
        company_id=company.id,
        external_id="demo-chat-001",
        channel=ConversationChannel.DASHBOARD,
    )

    assert upgraded.id == existing.id
    assert upgraded.channel == ConversationChannel.DASHBOARD.value


def test_get_or_create_preserves_web_channel_for_widget(
    conversation_repository: ConversationRepository,
    company: Company,
) -> None:
    existing = conversation_repository.create(
        company_id=company.id,
        external_id="widget-conv-1",
        channel=ConversationChannel.WEB,
    )

    same = conversation_repository.get_or_create_by_external_id(
        company_id=company.id,
        external_id="widget-conv-1",
        channel=ConversationChannel.WEB,
    )

    assert same.id == existing.id
    assert same.channel == ConversationChannel.WEB.value


def test_conversation_repository_scopes_by_company(
    conversation_repository: ConversationRepository,
    company_repository,
    company: Company,
) -> None:
    suffix = uuid4().hex[:8]
    other_company = company_repository.create(
        name=f"Other Co {suffix}",
        email=f"other-{suffix}@example.com",
    )
    conversation_repository.get_or_create_by_external_id(
        company_id=company.id,
        external_id="shared-external-id",
        channel=ConversationChannel.WEB,
    )
    conversation_repository.get_or_create_by_external_id(
        company_id=other_company.id,
        external_id="shared-external-id",
        channel=ConversationChannel.WEB,
    )

    tenant_conversation = conversation_repository.get_by_external_id(
        company_id=company.id,
        external_id="shared-external-id",
    )
    other_conversation = conversation_repository.get_by_external_id(
        company_id=other_company.id,
        external_id="shared-external-id",
    )

    assert tenant_conversation is not None
    assert other_conversation is not None
    assert tenant_conversation.id != other_conversation.id
