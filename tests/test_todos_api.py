import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_todos(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {
        "title": "Write tests",
        "description": "Create CRUD API tests",
    }
    create_response = await client.post(
        "/api/v1/todos/",
        json=payload,
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    created_todo = create_response.json()
    assert created_todo["id"] > 0
    assert created_todo["title"] == payload["title"]
    assert created_todo["description"] == payload["description"]
    assert created_todo["completed"] is False

    list_response = await client.get("/api/v1/todos/", headers=auth_headers)
    assert list_response.status_code == 200
    todos = list_response.json()
    assert len(todos) == 1
    assert todos[0]["id"] == created_todo["id"]


@pytest.mark.asyncio
async def test_get_todo_by_id_returns_404_when_missing(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.get("/api/v1/todos/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


@pytest.mark.asyncio
async def test_update_todo_by_id(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/todos/",
        json={"title": "Initial title", "description": "Initial description"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Updated title", "completed": True},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    updated_todo = update_response.json()
    assert updated_todo["id"] == todo_id
    assert updated_todo["title"] == "Updated title"
    assert updated_todo["description"] == "Initial description"
    assert updated_todo["completed"] is True


@pytest.mark.asyncio
async def test_delete_todo_by_id(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/todos/",
        json={"title": "Delete me", "description": None},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/todos/{todo_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_todos_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/todos/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_todo(
    client: AsyncClient,
    auth_headers: dict[str, str],
    another_auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/todos/",
        json={"title": "Private todo", "description": "owner A"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    get_response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers=another_auth_headers,
    )
    assert get_response.status_code == 403
