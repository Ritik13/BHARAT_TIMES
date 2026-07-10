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


def test_register_user_returns_created_user(client):
    payload = {"email": "user@example.com", "password": "secret123"}

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["id"] is not None


def test_login_returns_access_token(client):
    payload = {"email": "user@example.com", "password": "secret123"}
    client.post("/auth/register", json=payload)

    login_response = client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )

    assert login_response.status_code == 200
    token_data = login_response.json()
    assert token_data["token_type"] == "bearer"
    assert token_data["access_token"]
