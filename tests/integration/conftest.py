import os
from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.infrastructure.database.models import Base
from src.infrastructure.database.repositories import SQLAlchemyPostRepository
from src.infrastructure.mapper import PostModelMapper
from src.infrastructure.redis import RedisCache

load_dotenv(".env.test")

TEST_DATABASE_URL = os.getenv("DATABASE_URL")
TEST_REDIS_URL = os.getenv("REDIS_URL")


@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        db_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function") 
async def redis_client():
    client = await Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    await client.aclose()

@pytest.fixture(scope="function") 
async def redis_cache(redis_client):
    await redis_client.flushdb()
    yield RedisCache(redis_client, ttl=10)

@pytest.fixture
def post_model_mapper() -> PostModelMapper:
    return PostModelMapper()

@pytest.fixture
def post_repository(db_session, post_model_mapper) -> SQLAlchemyPostRepository:
    return SQLAlchemyPostRepository(db_session, post_model_mapper)



