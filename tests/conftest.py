import os
import sys
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Keep test imports resilient when no local .env exists.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_bootstrap.db")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault(
    "REFRESH_TOKEN_PEPPER",
    "test-refresh-token-pepper-at-least-32-chars",
)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import app.models.refresh_session  # noqa: F401
import app.models.todo  # noqa: F401
import app.models.user  # noqa: F401
from app.api.v1.routes import authentication, todos
from app.db.database import get_session


@pytest_asyncio.fixture
async def test_app(tmp_path: Path) -> AsyncGenerator[FastAPI, None]:
    db_path = tmp_path / "test.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        future=True,
        echo=False,
    )
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app = FastAPI()
    app.include_router(authentication.router, prefix="/api/v1", tags=["authentication"])
    app.include_router(todos.router, prefix="/api/v1/todos", tags=["todos"])
    app.dependency_overrides[get_session] = override_get_db

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield app

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as async_client:
        yield async_client


async def _create_auth_headers(client: AsyncClient) -> dict[str, str]:
    email = f"user_{uuid.uuid4().hex[:10]}@example.com"
    password = "Password123!"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201, register_response.text

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200, login_response.text

    access_token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    return await _create_auth_headers(client)


@pytest_asyncio.fixture
async def another_auth_headers(client: AsyncClient) -> dict[str, str]:
    return await _create_auth_headers(client)
