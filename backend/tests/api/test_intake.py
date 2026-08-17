import uuid
from uuid import UUID

from app.db.models.intake import IntakeItem
from app.repositories.company_repository import CompanyRepository
from app.repositories.intake_repository import IntakeRepository
from app.services.intake.email_parser import parse_email, source_sha256
from app.services.intake.models import IntakeStatus
from fastapi.testclient import TestClient
from tests.intake.conftest import FIXTURE_ROOT


def _create_intake_item(
    repository: IntakeRepository,
    *,
    company_id: UUID,
    case_id: str,
) -> IntakeItem:
    raw_message = (FIXTURE_ROOT / "cases" / case_id / "inquiry.eml").read_bytes()
    item, created = repository.create_received_email(
        company_id=company_id,
        email=parse_email(raw_message),
        source_sha256=source_sha256(raw_message),
        raw_message=raw_message,
    )
    assert created is True
    return item


def test_list_intake_items_requires_authentication(dev_client: TestClient) -> None:
    response = dev_client.get("/api/v1/intake-items")

    assert response.status_code == 401


def test_lists_only_current_tenant_items(
    dev_client: TestClient,
    auth_headers: dict[str, str],
    company,
    company_repository: CompanyRepository,
    intake_repository: IntakeRepository,
) -> None:
    own_item = _create_intake_item(
        intake_repository,
        company_id=company.id,
        case_id="case_006",
    )
    other_company = company_repository.create(
        name=f"Other Company {uuid.uuid4().hex[:8]}",
        email=f"other-{uuid.uuid4().hex[:8]}@example.com",
    )
    other_item = _create_intake_item(
        intake_repository,
        company_id=other_company.id,
        case_id="case_007",
    )

    response = dev_client.get("/api/v1/intake-items", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    ids = {item["id"] for item in body["items"]}
    assert str(own_item.id) in ids
    assert str(other_item.id) not in ids


def test_get_intake_item_is_tenant_scoped(
    dev_client: TestClient,
    auth_headers: dict[str, str],
    company_repository: CompanyRepository,
    intake_repository: IntakeRepository,
) -> None:
    other_company = company_repository.create(
        name=f"Private Company {uuid.uuid4().hex[:8]}",
        email=f"private-{uuid.uuid4().hex[:8]}@example.com",
    )
    other_item = _create_intake_item(
        intake_repository,
        company_id=other_company.id,
        case_id="case_008",
    )

    response = dev_client.get(
        f"/api/v1/intake-items/{other_item.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_reviews_downloads_and_exports_intake_item(
    dev_client: TestClient,
    auth_headers: dict[str, str],
    company,
    db_session,
    intake_repository: IntakeRepository,
) -> None:
    item = _create_intake_item(
        intake_repository,
        company_id=company.id,
        case_id="case_002",
    )
    intake_repository.apply_review(
        item,
        fields={},
        status=IntakeStatus.NEEDS_REVIEW,
    )

    review_response = dev_client.patch(
        f"/api/v1/intake-items/{item.id}/review",
        headers=auth_headers,
        json={
            "decision": "approve",
            "customer_name": "Tobias Hahn",
            "customer_email": "tobias@example.com",
            "service_requested": "Komplette Badsanierung",
            "service_address": {
                "street": "Musterweg 1",
                "postal_code": "50667",
                "city": "Köln",
            },
        },
    )

    assert review_response.status_code == 200
    assert review_response.json()["status"] == "ready"
    source_response = dev_client.get(
        f"/api/v1/intake-items/{item.id}/source.eml",
        headers=auth_headers,
    )
    assert source_response.status_code == 200
    assert b"Subject: Angebot fuer komplette Badsanierung" in source_response.content

    attachment = item.attachments[0]
    attachment_response = dev_client.get(
        f"/api/v1/intake-items/{item.id}/attachments/{attachment.id}",
        headers=auth_headers,
    )
    assert attachment_response.status_code == 200
    assert attachment_response.content.startswith(b"%PDF")

    export_response = dev_client.get(
        f"/api/v1/intake-items/{item.id}/export.csv",
        headers=auth_headers,
    )
    assert export_response.status_code == 200
    assert export_response.content.startswith(b"\xef\xbb\xbf")
    assert "Komplette Badsanierung" in export_response.content.decode("utf-8-sig")
    db_session.expire_all()
    assert (
        intake_repository.get_by_id(item.id, company_id=company.id).status
        == "exported"
    )


def test_requires_service_details_before_approval(
    dev_client: TestClient,
    auth_headers: dict[str, str],
    company,
    intake_repository: IntakeRepository,
) -> None:
    item = _create_intake_item(
        intake_repository,
        company_id=company.id,
        case_id="case_006",
    )
    intake_repository.apply_review(
        item,
        fields={},
        status=IntakeStatus.NEEDS_REVIEW,
    )

    response = dev_client.patch(
        f"/api/v1/intake-items/{item.id}/review",
        headers=auth_headers,
        json={"decision": "approve"},
    )

    assert response.status_code == 422
