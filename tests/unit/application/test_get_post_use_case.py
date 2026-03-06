import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from src.application.use_cases import GetPostUseCase
from src.application.dto import PostDTO
from src.domain.entities import Post
from src.application.exceptions import PostNotFoundError

@pytest.mark.asyncio
async def test_get_post_from_cache():
    post_id = uuid4()
    cached_dto = {"id": str(post_id), "title": "Post 1", "text": "Text"}

    mapper = MagicMock()
    mapper.dict_to_dto.return_value = PostDTO(
        id=post_id, title="Post 1", text="Text", created_at=None, updated_at=None
    )

    repo = AsyncMock()
    cache = AsyncMock()
    cache.get.return_value = cached_dto

    use_case = GetPostUseCase(mapper, repo, cache)

    result = await use_case(post_id)

    assert result.title == "Post 1"
    cache.get.assert_awaited_once_with(post_id)
    repo.get_by_id.assert_not_awaited()
    mapper.dict_to_dto.assert_called_once_with(cached_dto)


@pytest.mark.asyncio
async def test_get_post_from_db():
    post_id = uuid4()

    post = Post(id=post_id, title="DB", text="Text")
    post_dict = {"id": str(post_id), "title": "DB", "text": "Text"}

    mapper = MagicMock()

    mapper.to_dto.return_value = PostDTO(id=post_id, title="DB", text="Text", created_at=None, updated_at=None)
    mapper.to_dict.return_value = post_dict

    repo = AsyncMock()
    repo.get_by_id.return_value = post

    cache = AsyncMock()
    cache.get.return_value = None
    cache.set = AsyncMock()

    use_case = GetPostUseCase(mapper, repo, cache)

    result = await use_case(post_id)

    cache.get.assert_awaited_once_with(post_id)
    repo.get_by_id.assert_awaited_once_with(post_id)

    cache.set.assert_awaited_once_with(post_id, post_dict)

    assert result.title == "DB"
    assert result.text == "Text"

@pytest.mark.asyncio
async def test_post_not_found():
    post_id = uuid4()
    mapper = MagicMock()
    
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    
    cache = AsyncMock()
    cache.get.return_value = None

    use_case = GetPostUseCase(mapper, repo, cache)

    with pytest.raises(PostNotFoundError):
        await use_case(post_id)