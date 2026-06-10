import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.models.enums import ConversationChannel, MessageRole, UserRole
from app.main import app
from app.repositories.conversation_repository import ConversationRepository


@pytest.fixture
def other_company_auth_headers(dev_client: TestClient, user_repository, company_repository):
    suffix = uuid.uuid4().hex[:8]
    other_company = company_repository.create(
        name=f"Conversation Other Co {suffix}",
        email=f"conv-other-{suffix}@example.com",
    )
    user = user_repository.create(
        company_id=other_company.id,
        first_name="Other",
        last_name="User",
        email=f"conv-other-user-{suffix}@example.com",
        password_hash=hash_password("secure-password"),
        role=UserRole.MEMBER,
    )
    response = dev_client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "secure-password"},
    )
    assert response.status_code == 200
    return {
        "headers": {"Authorization": f"Bearer {response.json()['access_token']}"},
        "company_id": other_company.id,
    }


def test_list_conversation_messages_requires_auth(dev_client: TestClient) -> None:
    response = dev_client.get("/api/v1/conversations/demo-chat-001/messages")

    assert response.status_code == 401


def test_list_conversation_messages_returns_persisted_messages(
    dev_client: TestClient,
    conversation_repository: ConversationRepository,
    company,
    auth_headers: dict[str, str],
) -> None:
    conversation = conversation_repository.get_or_create_by_external_id(
        company_id=company.id,
        external_id="demo-chat-001",
        channel=ConversationChannel.WEB,
    )
    conversation_repository.add_message(
        conversation.id,
        MessageRole.USER,
        "I need a roofer",
    )
    conversation_repository.add_message(
        conversation.id,
        MessageRole.ASSISTANT,
        "Happy to help.",
    )

    response = dev_client.get(
        "/api/v1/conversations/demo-chat-001/messages",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["external_id"] == "demo-chat-001"
    assert body["channel"] == "web"
    assert len(body["messages"]) == 2
    assert body["messages"][0]["role"] == "user"
    assert body["messages"][1]["role"] == "assistant"


def test_list_conversation_messages_enforces_tenant_isolation(
    dev_client: TestClient,
    conversation_repository: ConversationRepository,
    company,
    auth_headers: dict[str, str],
    other_company_auth_headers: dict,
) -> None:
    conversation_repository.get_or_create_by_external_id(
        company_id=company.id,
        external_id="tenant-private-conv",
        channel=ConversationChannel.WEB,
    )

    response = dev_client.get(
        "/api/v1/conversations/tenant-private-conv/messages",
        headers=other_company_auth_headers["headers"],
    )

    assert response.status_code == 404
