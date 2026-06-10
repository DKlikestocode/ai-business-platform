import uuid

from fastapi.testclient import TestClient

from app.main import app


def _create_user(
    client: TestClient,
    *,
    email: str,
    password: str = "secure-password",
) -> dict:
    suffix = uuid.uuid4().hex[:8]
    company = client.post(
        "/api/v1/companies",
        json={
            "name": f"Auth Test Co {suffix}",
            "email": f"auth-co-{suffix}@example.com",
        },
    )
    assert company.status_code == 201

    response = client.post(
        "/api/v1/users",
        json={
            "company_id": company.json()["id"],
            "first_name": "Auth",
            "last_name": "User",
            "email": email,
            "password": password,
            "role": "member",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_login_success_returns_access_token() -> None:
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    email = f"login-success-{suffix}@example.com"
    password = "secure-password"
    user = _create_user(client, email=email, password=password)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 30 * 60

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me_response.status_code == 200
    me_body = me_response.json()
    assert me_body["id"] == user["id"]
    assert me_body["email"] == email
    assert "password" not in me_body
    assert "password_hash" not in me_body


def test_login_rejects_invalid_password() -> None:
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    email = f"login-wrong-pass-{suffix}@example.com"
    _create_user(client, email=email, password="secure-password")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_rejects_unknown_user() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing.user@example.com",
            "password": "secure-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_me_returns_current_user_with_valid_token() -> None:
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    email = f"me-valid-{suffix}@example.com"
    password = "secure-password"
    user = _create_user(client, email=email, password=password)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == user["id"]
    assert body["company_id"] == user["company_id"]
    assert body["first_name"] == "Auth"
    assert body["last_name"] == "User"
    assert body["email"] == email
    assert body["role"] == "member"
    assert body["is_active"] is True


def test_me_requires_authentication() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated."


def test_me_rejects_invalid_token() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token."
