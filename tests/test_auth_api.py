import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token(client: AsyncClient) -> None:
    email = "refresh_user@example.com"
    password = "Password123!"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token_pair = login_response.json()

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_pair["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    payload = refresh_response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["refresh_token"] != token_pair["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_reuse_detection_revokes_family(client: AsyncClient) -> None:
    email = "refresh_reuse_user@example.com"
    password = "Password123!"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    refresh_token_1 = login_response.json()["refresh_token"]

    refresh_response_1 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_1},
    )
    assert refresh_response_1.status_code == 200
    refresh_token_2 = refresh_response_1.json()["refresh_token"]

    reuse_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_1},
    )
    assert reuse_response.status_code == 401

    family_revoked_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_2},
    )
    assert family_revoked_response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rejects_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not-a-valid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_accepts_valid_refresh_token(client: AsyncClient) -> None:
    email = "logout_user@example.com"
    password = "Password123!"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_response.status_code == 204

    refresh_after_logout = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_after_logout.status_code == 401


@pytest.mark.asyncio
async def test_logout_rejects_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": "invalid-token"},
    )
    assert response.status_code == 401
