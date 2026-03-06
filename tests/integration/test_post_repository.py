import pytest
from uuid import uuid4
from src.domain.entities import Post

@pytest.mark.asyncio
async def test_save_and_get_by_id(post_repository):
    post_id = uuid4()
    post = Post(id=post_id, title="Post #1", text="Text")

    await post_repository.save(post)
    found = await post_repository.get_by_id(post_id)

    assert found is not None
    assert found.id == post_id
    assert found.title == "Post #1"
    assert found.text == "Text"
    assert found.created_at is not None
    assert found.updated_at is None

@pytest.mark.asyncio
async def test_update(post_repository):
    post_id = uuid4()
    post = Post(id=post_id, title="Post №1", text="Text")
    await post_repository.save(post)

    post.update(title="Post #2", text="Text #2")
    await post_repository.update(post)

    updated = await post_repository.get_by_id(post_id)
    assert updated.title == "Post #2"
    assert updated.text == "Text #2"
    assert updated.updated_at is not None

@pytest.mark.asyncio
async def test_delete(post_repository):
    post_id = uuid4()
    post = Post(id=post_id, title="Post #1", text="Text")
    await post_repository.save(post)

    deleted = await post_repository.delete(post_id)
    assert deleted is True

    found = await post_repository.get_by_id(post_id)
    assert found is None

@pytest.mark.asyncio
async def test_get_by_id_not_found(post_repository):
    random_id = uuid4()
    found = await post_repository.get_by_id(random_id)
    assert found is None

