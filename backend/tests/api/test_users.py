import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_create_user_returns_201_without_password_hash() -> None:
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    company = client.post(
        "/api/v1/companies",
        json={"name": f"User Test Co {suffix}", "email": f"users-{suffix}@example.com"},
    ).json()

    response = client.post(
        "/api/v1/users",
        json={
            "company_id": company["id"],
            "first_name": "Anna",
            "last_name": "Admin",
            "email": f"anna.admin-{suffix}@example.com",
            "password": "secure-password",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["company_id"] == company["id"]
    assert body["first_name"] == "Anna"
    assert body["last_name"] == "Admin"
    assert body["email"] == f"anna.admin-{suffix}@example.com"
    assert body["role"] == "admin"
    assert body["is_active"] is True
    assert "password_hash" not in body
    assert "password" not in body


def test_create_user_requires_existing_company() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/users",
        json={
            "company_id": "00000000-0000-0000-0000-000000000099",
            "first_name": "Ghost",
            "last_name": "User",
            "email": "ghost@example.com",
            "password": "secure-password",
        },
    )

    assert response.status_code == 404


def test_create_user_rejects_duplicate_email() -> None:
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    company = client.post(
        "/api/v1/companies",
        json={"name": f"Duplicate User Co {suffix}", "email": f"dup-{suffix}@example.com"},
    ).json()
    payload = {
        "company_id": company["id"],
        "first_name": "First",
        "last_name": "User",
        "email": f"same.user-{suffix}@example.com",
        "password": "secure-password",
    }

    first = client.post("/api/v1/users", json=payload)
    second = client.post("/api/v1/users", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_create_user_validates_password_length() -> None:
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    company = client.post(
        "/api/v1/companies",
        json={"name": f"Validation Co {suffix}", "email": f"validation-{suffix}@example.com"},
    ).json()

    response = client.post(
        "/api/v1/users",
        json={
            "company_id": company["id"],
            "first_name": "Short",
            "last_name": "Pass",
            "email": f"short-{suffix}@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422
