import uuid

import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.models import LeadExtractedData
from app.agents.lead_agent.repository import LeadRepository
from app.core.security import hash_password
from app.db.models.company import Company
from app.db.models.enums import UserRole
from app.main import app


@pytest.fixture
def other_company(company_repository):
    suffix = uuid.uuid4().hex[:8]
    return company_repository.create(
        name=f"Other Company {suffix}",
        email=f"other-{suffix}@example.com",
    )


@pytest.fixture
def other_company_auth_headers(dev_client: TestClient, user_repository, other_company):
    suffix = uuid.uuid4().hex[:8]
    user = user_repository.create(
        company_id=other_company.id,
        first_name="Other",
        last_name="User",
        email=f"other-user-{suffix}@example.com",
        password_hash=hash_password("secure-password"),
        role=UserRole.MEMBER,
    )
    response = dev_client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "secure-password"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_list_leads_scopes_to_authenticated_tenant(
    dev_client: TestClient,
    lead_repository: LeadRepository,
    company: Company,
    other_company: Company,
    auth_headers: dict[str, str],
) -> None:
    lead_repository.create(
        company_id=company.id,
        conversation_id="tenant-scope-a",
        data=LeadExtractedData(
            name="Tenant Lead",
            phone="01701234567",
            location="Berlin",
            service_requested="HVAC",
            description="Test",
            urgency="low",
            preferred_callback_time="Morning",
        ),
        summary=None,
    )
    lead_repository.create(
        company_id=other_company.id,
        conversation_id="tenant-scope-b",
        data=LeadExtractedData(
            name="Other Tenant Lead",
            phone="01701234600",
            location="Munich",
            service_requested="Plumbing",
            description="Test",
            urgency="high",
            preferred_callback_time="Afternoon",
        ),
        summary=None,
    )

    response = dev_client.get("/api/v1/leads", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert all(item["company_id"] == str(company.id) for item in body["items"])
    assert all(item["name"] != "Other Tenant Lead" for item in body["items"])


def test_get_lead_rejects_cross_tenant_access(
    dev_client: TestClient,
    lead_repository: LeadRepository,
    other_company: Company,
    auth_headers: dict[str, str],
) -> None:
    lead = lead_repository.create(
        company_id=other_company.id,
        conversation_id="cross-tenant-lead",
        data=LeadExtractedData(
            name="Hidden Lead",
            phone="01701234700",
            location="Hamburg",
            service_requested="Electrical",
            description="Test",
            urgency="medium",
            preferred_callback_time="Evening",
        ),
        summary=None,
    )

    response = dev_client.get(f"/api/v1/leads/{lead.id}", headers=auth_headers)

    assert response.status_code == 404


def test_get_company_rejects_other_tenant(
    dev_client: TestClient,
    other_company: Company,
    auth_headers: dict[str, str],
) -> None:
    response = dev_client.get(
        f"/api/v1/companies/{other_company.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404
