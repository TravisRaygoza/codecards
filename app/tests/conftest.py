import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.main import app
from app.database.session import get_session
from app.config import db_settings


def ensure_test_database_exists():
    """Create the test database if it doesn't exist (idempotent)."""
    conn = psycopg2.connect(
        host=db_settings.POSTGRES_SERVER,
        port=db_settings.POSTGRES_PORT,
        user=db_settings.POSTGRES_USER,
        password=db_settings.POSTGRES_PASSWORD,
        dbname=db_settings.POSTGRES_DB,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    test_db = f"{db_settings.POSTGRES_DB}_test"
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (test_db,))
    if not cursor.fetchone():
        cursor.execute(f'CREATE DATABASE "{test_db}"')
    cursor.close()
    conn.close()


ensure_test_database_exists()

# Use a separate test database
TEST_DB_URL = f"postgresql+asyncpg://{db_settings.POSTGRES_USER}:{db_settings.POSTGRES_PASSWORD}@{db_settings.POSTGRES_SERVER}:{db_settings.POSTGRES_PORT}/{db_settings.POSTGRES_DB}_test"

# NullPool = each session gets its own fresh connection, no reuse
# This prevents "another operation is in progress" errors
test_engine = create_async_engine(TEST_DB_URL, echo=False, poolclass=NullPool)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables before tests, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def client():
    """Provide a test HTTP client with overridden database session."""

    async def override_get_session():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # Mock Redis cache functions so tests don't need a running Redis
    with (
        patch("app.services.deck.cache_get", new_callable=AsyncMock, return_value=None),
        patch("app.services.deck.cache_set", new_callable=AsyncMock),
        patch("app.services.deck.cache_delete_pattern", new_callable=AsyncMock),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client):
    """Provide an authenticated test client."""
    # Create a test user
    user_data = {
        "username": f"testuser_{uuid4().hex[:8]}",
        "email": f"test_{uuid4().hex[:8]}@test.com",
        "password": "testpassword123",
    }
    await client.post("/user/signup", json=user_data)

    # Login to get token
    login_response = await client.post(
        "/user/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    token = login_response.json()["access_token"]

    # Set auth header for all future requests
    client.headers["Authorization"] = f"Bearer {token}"

    return client
