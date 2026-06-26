import pytest
from fastapi.testclient import TestClient

from app.agents.lead_agent.models import LeadExtractedData, LeadStatus
from app.agents.lead_agent.qualification import evaluate_qualification
from app.agents.lead_agent.repository import LeadRepository
from app.db.models.company import Company
from app.db.models.enums import ConversationChannel
from app.main import app


@pytest.fixture
def sample_leads(lead_repository: LeadRepository, company: Company) -> list:
    leads = []
    payloads = [
        ("conv-a", "Alice", LeadStatus.NEW),
        ("conv-b", "Bob", LeadStatus.CONTACTED),
        ("conv-c", "Carol", LeadStatus.QUALIFIED),
        ("conv-d", "Dan", LeadStatus.WON),
        ("conv-e", "Eve", LeadStatus.LOST),
    ]
    for conversation_id, name, _ in payloads:
        leads.append(
            lead_repository.create(
                company_id=company.id,
                conversation_id=conversation_id,
                data=LeadExtractedData(
                    name=name,
                    phone="01701234567",
                    location="Austin, TX",
                    postal_code="10115",
                    service_requested="HVAC",
                    description="Needs service",
                    urgency="medium",
                    preferred_callback_time="Morning",
                ),
                summary=f"{name} lead",
            )
        )

    lead_repository.update_status(leads[1].id, LeadStatus.CONTACTED, company_id=company.id)
    lead_repository.update_status(leads[2].id, LeadStatus.QUALIFIED, company_id=company.id)
    lead_repository.update_status(leads[3].id, LeadStatus.WON, company_id=company.id)
    lead_repository.update_status(leads[4].id, LeadStatus.LOST, company_id=company.id)
    return leads


@pytest.fixture
def dashboard_client() -> TestClient:
    return TestClient(app)


def test_list_leads_requires_authentication(dashboard_client: TestClient) -> None:
    response = dashboard_client.get("/api/v1/leads?page=1&page_size=2")

    assert response.status_code == 401


def test_list_leads_returns_paginated_response(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    response = dashboard_client.get(
        "/api/v1/leads?page=1&page_size=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total"] == 1
    assert body["total_pages"] == 1
    assert len(body["items"]) == 1
    assert "id" in body["items"][0]
    assert "company_id" in body["items"][0]
    assert "status" in body["items"][0]


def test_list_leads_filters_by_status(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    response = dashboard_client.get(
        "/api/v1/leads?status=contacted&archived=true",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert all(item["status"] == "contacted" for item in body["items"])


def test_list_leads_sorted_by_created_at_descending(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    response = dashboard_client.get(
        "/api/v1/leads?page=1&page_size=10",
        headers=auth_headers,
    )

    assert response.status_code == 200
    created_times = [item["created_at"] for item in response.json()["items"]]
    assert created_times == sorted(created_times, reverse=True)


def test_get_lead_by_id(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    lead = sample_leads[0]
    response = dashboard_client.get(
        f"/api/v1/leads/{lead.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(lead.id)
    assert body["name"] == "Alice"
    assert body["status"] == "new"


def test_get_lead_not_found(
    dashboard_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = dashboard_client.get(
        "/api/v1/leads/00000000-0000-0000-0000-000000000099",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_update_lead_status_rejects_legacy_status(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    lead = sample_leads[0]
    response = dashboard_client.patch(
        f"/api/v1/leads/{lead.id}/status",
        json={"status": "qualified"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_update_lead_status_sets_contacted_at(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    lead = sample_leads[0]
    response = dashboard_client.patch(
        f"/api/v1/leads/{lead.id}/status",
        json={"status": "contacted"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "contacted"
    assert body["contacted_at"] is not None


def test_update_lead_status_not_found(
    dashboard_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = dashboard_client.patch(
        "/api/v1/leads/00000000-0000-0000-0000-000000000099/status",
        json={"status": "contacted"},
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_list_leads_filters_by_qualification_status(
    dashboard_client: TestClient,
    lead_repository: LeadRepository,
    company: Company,
    auth_headers: dict[str, str],
) -> None:
    complete_data = LeadExtractedData(
        name="Qualified Lead",
        phone="01701234567",
        location="Austin, TX",
        postal_code="10115",
        service_requested="HVAC",
        description="Needs service",
        urgency="medium",
        preferred_callback_time="Morning",
    )
    lead_repository.create(
        company_id=company.id,
        conversation_id="qual-filter-complete",
        data=complete_data,
        summary="Qualified lead",
        qualification=evaluate_qualification(complete_data, channel=ConversationChannel.WEB),
    )

    response = dashboard_client.get(
        "/api/v1/leads?qualification_status=qualified",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert all(item["qualification_status"] == "qualified" for item in body["items"])


def test_list_leads_filters_by_contactable(
    dashboard_client: TestClient,
    lead_repository: LeadRepository,
    company: Company,
    auth_headers: dict[str, str],
) -> None:
    contactable_data = LeadExtractedData(
        name="Contactable Lead",
        phone="01701234600",
        location="Austin, TX",
        postal_code="10115",
        service_requested="Plumbing",
        description="Leak in kitchen",
    )
    lead_repository.create(
        company_id=company.id,
        conversation_id="contactable-filter",
        data=contactable_data,
        summary="Contactable lead",
        qualification=evaluate_qualification(contactable_data, channel=ConversationChannel.WEB),
    )

    response = dashboard_client.get(
        "/api/v1/leads?contactable=true",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert all(item["contactable"] is True for item in body["items"])


def test_list_leads_sorted_by_urgency_descending(
    dashboard_client: TestClient,
    lead_repository: LeadRepository,
    company: Company,
    auth_headers: dict[str, str],
) -> None:
    for urgency, conversation_id in (
        ("niedrig", "sort-urgency-low"),
        ("hoch", "sort-urgency-high"),
        ("mittel", "sort-urgency-medium"),
    ):
        data = LeadExtractedData(
            name=f"Lead {urgency}",
            phone="01701234700",
            urgency=urgency,
        )
        lead_repository.create(
            company_id=company.id,
            conversation_id=conversation_id,
            data=data,
            summary=f"Urgency {urgency}",
            qualification=evaluate_qualification(data, channel=ConversationChannel.WEB),
        )

    response = dashboard_client.get(
        "/api/v1/leads?sort=urgency_desc&page_size=50",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()["items"]
    test_items = [
        item for item in items if item["name"].startswith("Lead ")
    ]
    assert [item["urgency"] for item in test_items] == ["hoch", "mittel", "niedrig"]


def test_get_lead_includes_qualification_fields(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    lead = sample_leads[0]
    response = dashboard_client.get(
        f"/api/v1/leads/{lead.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert "contactable" in body
    assert "contact_method" in body
    assert "lead_score" in body
    assert "qualification_status" in body
    assert "notification_sent_at" in body


def test_update_lead_status_rejects_invalid_status(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    lead = sample_leads[0]
    response = dashboard_client.patch(
        f"/api/v1/leads/{lead.id}/status",
        json={"status": "invalid-status"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_update_lead_status_archives_non_new_lead(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    lead = sample_leads[0]
    response = dashboard_client.patch(
        f"/api/v1/leads/{lead.id}/status",
        json={"status": "contacted"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["archived_at"] is not None

    active = dashboard_client.get("/api/v1/leads", headers=auth_headers)
    assert active.status_code == 200
    assert all(item["id"] != str(lead.id) for item in active.json()["items"])


def test_list_contacted_leads_and_restore(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    lead = sample_leads[1]
    archived = dashboard_client.get(
        "/api/v1/leads?archived=true",
        headers=auth_headers,
    )
    assert archived.status_code == 200
    assert archived.json()["total"] >= 4
    assert any(item["id"] == str(lead.id) for item in archived.json()["items"])

    restore = dashboard_client.patch(
        f"/api/v1/leads/{lead.id}/restore",
        headers=auth_headers,
    )
    assert restore.status_code == 200
    assert restore.json()["status"] == "new"
    assert restore.json()["archived_at"] is None
    assert restore.json()["contacted_at"] is None

    active = dashboard_client.get("/api/v1/leads", headers=auth_headers)
    assert any(item["id"] == str(lead.id) for item in active.json()["items"])


def test_delete_lead(
    dashboard_client: TestClient,
    sample_leads,
    auth_headers: dict[str, str],
) -> None:
    lead = sample_leads[0]
    response = dashboard_client.delete(
        f"/api/v1/leads/{lead.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    get_response = dashboard_client.get(
        f"/api/v1/leads/{lead.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


def test_delete_lead_not_found(
    dashboard_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = dashboard_client.delete(
        "/api/v1/leads/00000000-0000-0000-0000-000000000099",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_delete_all_contacted_leads(
    dashboard_client: TestClient,
    lead_repository: LeadRepository,
    company: Company,
    auth_headers: dict[str, str],
) -> None:
    active_data = LeadExtractedData(name="Active Lead", phone="01701234701")
    contacted_data = LeadExtractedData(name="Contacted Lead", phone="01701234702")
    active = lead_repository.create(
        company_id=company.id,
        conversation_id="bulk-delete-active",
        data=active_data,
        summary="Active",
        qualification=evaluate_qualification(active_data, channel=ConversationChannel.WEB),
    )
    contacted = lead_repository.create(
        company_id=company.id,
        conversation_id="bulk-delete-contacted",
        data=contacted_data,
        summary="Contacted",
        qualification=evaluate_qualification(contacted_data, channel=ConversationChannel.WEB),
    )
    lead_repository.update_status(
        contacted.id,
        LeadStatus.CONTACTED,
        company_id=company.id,
    )

    response = dashboard_client.delete(
        "/api/v1/leads/contacted",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["deleted"] >= 1

    assert lead_repository.get_by_id(active.id, company_id=company.id) is not None

    get_contacted = dashboard_client.get(
        f"/api/v1/leads/{contacted.id}",
        headers=auth_headers,
    )
    assert get_contacted.status_code == 404
