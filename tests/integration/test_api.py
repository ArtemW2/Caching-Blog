import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from src.presentation.dependencies import get_db_session, get_redis_session


@pytest.fixture
async def async_client(db_session, redis_client):
    def override_get_db():
        return db_session

    def override_get_redis():
        return redis_client

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_redis_session] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_post(async_client):
    response = await async_client.post(
        "/posts/", json={"title": "Post №1", "text": "Text"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Post №1"
    assert data["text"] == "Text"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_post(async_client):
    create_resp = await async_client.post(
        "/posts/", json={"title": "Post №1", "text": "Hello World"}
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    get_resp = await async_client.get(f"/posts/{post_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["title"] == "Post №1"
    assert data["text"] == "Hello World"
    assert data["id"] == post_id


@pytest.mark.asyncio
async def test_get_post_not_found(async_client):
    post_id = "00000000-0000-0000-0000-000000000000"
    response = await async_client.get(f"/posts/{post_id}")
    assert response.status_code == 404
    assert "интересующая вас публикация не найдена" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_post(async_client):
    create_resp = await async_client.post(
        "/posts/", json={"title": "Post 1", "text": "Text"}
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    update_resp = await async_client.patch(
        f"/posts/{post_id}", json={"title": "Post 2", "text": "Text 2"}
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["title"] == "Post 2"
    assert updated_data["text"] == "Text 2"
    assert updated_data["id"] == post_id

    get_resp = await async_client.get(f"/posts/{post_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Post 2"
    assert get_resp.json()["text"] == "Text 2"


@pytest.mark.asyncio
async def test_delete_post(async_client):
    create_resp = await async_client.post(
        "/posts/", json={"title": "Post", "text": "Text"}
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    delete_resp = await async_client.delete(f"/posts/{post_id}")
    assert delete_resp.status_code == 204  

    get_resp = await async_client.get(f"/posts/{post_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_cache_behavior(async_client, redis_client):
    create_resp = await async_client.post("/posts/", json={"title": "Post #1", "text": "Text"})
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    first = await async_client.get(f"/posts/{post_id}")
    assert first.status_code == 200
    first_data = first.json()

    cached = await redis_client.get(str(post_id))
    assert cached is not None

    second = await async_client.get(f"/posts/{post_id}")
    assert second.status_code == 200
    assert second.json() == first_data

    update_resp = await async_client.patch(
        f"/posts/{post_id}", json={"title": "Post 2", "text": "Text 2"}
    )
    assert update_resp.status_code == 200

    cached_after_update = await redis_client.get(str(post_id))
    assert cached_after_update is None

    third = await async_client.get(f"/posts/{post_id}")
    assert third.status_code == 200
    assert third.json()["title"] == "Post 2"
    assert third.json()["text"] == "Text 2"
    assert third.json() != first_data

    cached_final = await redis_client.get(str(post_id))
    assert cached_final is not None