import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_create_company_returns_201() -> None:
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    response = client.post(
        "/api/v1/companies",
        json={
            "name": f"Acme GmbH {suffix}",
            "email": f"contact-{suffix}@acme.example",
            "phone": "+49 30 123456",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == f"Acme GmbH {suffix}"
    assert body["slug"] == f"acme-gmbh-{suffix}"
    assert body["email"] == f"contact-{suffix}@acme.example"
    assert body["phone"] == "+49 30 123456"
    assert "id" in body
    assert "created_at" in body


def test_get_company_by_id(dev_client: TestClient, company, auth_headers: dict[str, str]) -> None:
    response = dev_client.get(
        f"/api/v1/companies/{company.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(company.id)


def test_get_company_not_found(
    dev_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = dev_client.get(
        "/api/v1/companies/00000000-0000-0000-0000-000000000099",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_create_company_generates_unique_slug() -> None:
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    name = f"Duplicate Name {suffix}"
    first = client.post(
        "/api/v1/companies",
        json={"name": name, "email": f"first-{suffix}@example.com"},
    )
    second = client.post(
        "/api/v1/companies",
        json={"name": name, "email": f"second-{suffix}@example.com"},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["slug"] == f"duplicate-name-{suffix}"
    assert second.json()["slug"] == f"duplicate-name-{suffix}-1"
