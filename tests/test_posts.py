import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from database import AsyncSessionLocal
from main import app


@pytest.fixture(autouse=True)
def clear_posts_table():
    async def _clear():
        async with AsyncSessionLocal() as session:
            await session.execute(text("DELETE FROM posts"))
            await session.commit()

    asyncio.run(_clear())
    yield
    asyncio.run(_clear())


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


def test_create_post_returns_201_and_persisted_data(client):
    payload = {
        "title": "My first post",
        "content": "This is the body of the post",
        "published": True,
    }

    response = client.post("/posts/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["published"] is True
    assert data["id"] is not None


def test_get_all_posts_can_filter_by_published_status(client):
    client.post(
        "/posts/",
        json={
            "title": "Published post",
            "content": "Published body content",
            "published": True,
        },
    )
    client.post(
        "/posts/",
        json={
            "title": "Draft post",
            "content": "Draft body content",
            "published": False,
        },
    )

    published_response = client.get("/posts/?published=true")
    draft_response = client.get("/posts/?published=false")

    assert published_response.status_code == 200
    assert draft_response.status_code == 200
    assert len(published_response.json()) == 1
    assert len(draft_response.json()) == 1
    assert published_response.json()[0]["title"] == "Published post"
    assert draft_response.json()[0]["title"] == "Draft post"


def test_create_post_rejects_blank_title(client):
    response = client.post(
        "/posts/",
        json={
            "title": "   ",
            "content": "This is a valid content",
            "published": False,
        },
    )

    assert response.status_code == 422


def test_get_missing_post_returns_404(client):
    response = client.get("/posts/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"
