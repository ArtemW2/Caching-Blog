from typing import Any, AsyncGenerator

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import CacheStorage
from src.application.mapper import PostMapper
from src.application.use_cases import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetPostUseCase,
    UpdatePostUseCase,
)
from src.domain.factories import PostFactory
from src.domain.interfaces import PostRepository
from src.infrastructure.database.repositories import SQLAlchemyPostRepository
from src.infrastructure.mapper import PostModelMapper
from src.infrastructure.redis import RedisCache


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, Any]:
    async_session_maker = request.app.state.async_session_maker
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_redis_session(request: Request):
    return request.app.state.redis


def get_mapper() -> PostMapper:
    return PostMapper()


def get_model_mapper() -> PostModelMapper:
    return PostModelMapper()


def get_repo(
    session: AsyncSession = Depends(get_db_session),
    mapper: PostModelMapper = Depends(get_model_mapper),
) -> PostRepository:
    return SQLAlchemyPostRepository(session, mapper)


def get_factory() -> PostFactory:
    return PostFactory()


def get_cache(redis: Redis = Depends(get_redis_session)) -> CacheStorage:
    return RedisCache(redis)


def create_post_use_case(
    mapper: PostMapper = Depends(get_mapper),
    repo: PostRepository = Depends(get_repo),
    factory: PostFactory = Depends(get_factory),
) -> CreatePostUseCase:
    return CreatePostUseCase(mapper, repo, factory)


def get_post_use_case(
    mapper: PostMapper = Depends(get_mapper),
    repo: PostRepository = Depends(get_repo),
    cache: CacheStorage = Depends(get_cache),
) -> GetPostUseCase:
    return GetPostUseCase(mapper, repo, cache)


def update_post_use_case(
    mapper: PostMapper = Depends(get_mapper),
    repo: PostRepository = Depends(get_repo),
    cache: CacheStorage = Depends(get_cache),
) -> UpdatePostUseCase:
    return UpdatePostUseCase(mapper, repo, cache)


def delete_post_use_case(
    repo: PostRepository = Depends(get_repo),
    cache: CacheStorage = Depends(get_cache),
) -> DeletePostUseCase:
    return DeletePostUseCase(repo, cache)
