import asyncio
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from database import AsyncSessionLocal
from main import app


@pytest.fixture(autouse=True)
def clear_users_table():
    async def _clear():
        async with AsyncSessionLocal() as session:
            await session.execute(text("DELETE FROM users"))
            await session.commit()

    asyncio.run(_clear())
    yield
    asyncio.run(_clear())


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


def test_register_and_login_flow(client):
    payload = {
        "email": "user@example.com",
        "password": "secret123",
    }

    register_response = client.post("/auth/register", json=payload)
    assert register_response.status_code == 200

    register_data = register_response.json()
    assert register_data["email"] == payload["email"]
    assert register_data["id"] is not None

    login_response = client.post("/auth/login", json=payload)
    assert login_response.status_code == 200

    token_data = login_response.json()
    assert token_data["token_type"] == "bearer"
    assert token_data["access_token"]
