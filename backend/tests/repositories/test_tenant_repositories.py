from app.db.models.company import Company
from app.db.models.enums import ConversationChannel
from app.repositories.agent_repository import AgentRepository
from app.repositories.conversation_repository import ConversationRepository


def test_conversation_repository_scopes_by_company(
    conversation_repository: ConversationRepository,
    company: Company,
) -> None:
    conversation = conversation_repository.get_or_create_by_external_id(
        company_id=company.id,
        external_id="conv-123",
        channel=ConversationChannel.WEB,
    )

    assert conversation.company_id == company.id
    assert conversation.external_id == "conv-123"
    assert (
        conversation_repository.get_by_external_id(
            company_id=company.id,
            external_id="conv-123",
        )
        is not None
    )


def test_agent_repository_scopes_by_company(
    agent_repository: AgentRepository,
    company: Company,
) -> None:
    agent = agent_repository.create(
        company_id=company.id,
        name="Lead Capture",
        agent_type="lead_capture",
    )

    assert agent.company_id == company.id
    assert (
        agent_repository.get_by_type(
            company_id=company.id,
            agent_type="lead_capture",
        )
        is not None
    )
