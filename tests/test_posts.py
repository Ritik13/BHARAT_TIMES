import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from database import AsyncSessionLocal
from main import app


@pytest.fixture(autouse=True)
def clear_tables():
    async def _clear():
        async with AsyncSessionLocal() as session:
            await session.execute(text("DELETE FROM posts"))
            await session.execute(text("DELETE FROM users"))
            await session.commit()

    asyncio.run(_clear())
    yield
    asyncio.run(_clear())


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def auth_headers(client):
    user = {
        "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
        "password": "secret123",
    }
    register_response = client.post("/auth/register", json=user)
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_post_requires_auth_and_returns_post(client, auth_headers):
    payload = {
        "title": "Simple post",
        "content": "This is a simple post body.",
        "published": True,
    }

    response = client.post("/posts/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["published"] is True
    assert data["id"] is not None


def test_get_missing_post_returns_404(client):
    response = client.get("/posts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"
