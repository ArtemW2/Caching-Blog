import pytest
from uuid import uuid4
from unittest.mock import MagicMock, AsyncMock
from src.domain.entities import Post
from src.application.dto import UpdatePostDTO, PostDTO
from src.application.use_cases import UpdatePostUseCase
from src.application.exceptions import PostNotFoundError, CacheError

@pytest.mark.asyncio
async def test_update_post_use_case():
    post_id = uuid4()

    original_post = Post(post_id, title="Post №1", text="HELLO WORLD")
    
    update_dto = UpdatePostDTO(title="Post #2", text="Good bye")
    expected_dto = PostDTO(
        id=post_id, title="Post #2", text="Good bye", created_at=None, updated_at=None
    )

    mapper = MagicMock()
    mapper.to_dto.return_value = expected_dto


    repo = AsyncMock()
    repo.get_by_id.return_value = original_post
    repo.update = AsyncMock()

    cache = AsyncMock()
    cache.invalidate = AsyncMock()

    use_case = UpdatePostUseCase(mapper, repo, cache)

    result = await use_case(post_id, update_dto)

    repo.get_by_id.assert_awaited_once_with(post_id)
    assert original_post.title == "Post #2"
    assert original_post.text == "Good bye"

    repo.update.assert_awaited_once_with(original_post)
    cache.invalidate.assert_awaited_once_with(post_id)
    mapper.to_dto.assert_called_once_with(original_post)
    assert result == expected_dto

@pytest.mark.asyncio
async def test_update_post_use_case_not_found():
    post_id = uuid4()
    update_dto = UpdatePostDTO(title="Post #2", text="Good bye")

    mapper = MagicMock()
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    cache = AsyncMock()

    use_case = UpdatePostUseCase(mapper, repo, cache)

    with pytest.raises(PostNotFoundError):
        await use_case(post_id, update_dto)

    repo.get_by_id.assert_awaited_once_with(post_id)
    repo.update.assert_not_awaited()
    cache.invalidate.assert_not_awaited()

@pytest.mark.asyncio
async def test_update_post_use_case_cache_error():
    post_id = uuid4()
    original_post = Post(id=post_id, title="Post №1", text="HELLO WORLD")
    update_dto = UpdatePostDTO(title="Post #2", text="Good bye")

    mapper = MagicMock()
    mapper.to_dto.return_value = PostDTO(
        id=post_id, title="Post #2", text="Good bye", created_at=None, updated_at=None
    )

    repo = AsyncMock()
    repo.get_by_id.return_value = original_post
    repo.update = AsyncMock()

    cache = AsyncMock()
    cache.invalidate.side_effect = CacheError("Redis недоступен")

    use_case = UpdatePostUseCase(mapper, repo, cache)

    result = await use_case(post_id, update_dto)

    repo.update.assert_awaited_once_with(original_post)
    cache.invalidate.assert_awaited_once_with(post_id)
    assert result is not None