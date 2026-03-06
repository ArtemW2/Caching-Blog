from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.application.exceptions import PostNotFoundError
from src.config import settings
from src.domain.exceptions import PostTitleError, PostDataError
from src.infrastructure.database.session import create_db_engine, get_session_factory
from src.infrastructure.exceptions import (
    DatabaseConnectionError,
    DatabaseError,
    DatabaseIntegrityError,
)
from src.presentation.api.posts import post_router
from src.presentation.handlers import (
    database_connection_handler,
    database_handler,
    database_integrity_handler,
    invalid_post_content_handler,
    post_data_handler,
    post_not_found_handler,
)
from src.presentation.middleware import RateLimitMiddleware

from src.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine: AsyncEngine = create_db_engine(settings.DATABASE_URL)
    async_session_maker: async_sessionmaker[AsyncSession] = get_session_factory(engine)

    app.state.engine = engine
    app.state.async_session_maker = async_session_maker

    try:
        redis: Redis = await Redis.from_url(settings.REDIS_URL)
        app.state.redis = redis
    except Exception as e:
        logger.error(f"Не удалось установить соединение с Redis: {e}. Кэш недоступен")
        app.state.redis = None

    yield

    await engine.dispose()
    
    if app.state.redis:
        await redis.close()


app = FastAPI(lifespan=lifespan)
app.include_router(post_router)

app.add_middleware(RateLimitMiddleware, calls=20, period=30)

app.add_exception_handler(PostDataError, post_data_handler)
app.add_exception_handler(PostTitleError, invalid_post_content_handler)
app.add_exception_handler(PostNotFoundError, post_not_found_handler)
app.add_exception_handler(DatabaseConnectionError, database_connection_handler)
app.add_exception_handler(DatabaseError, database_handler)
app.add_exception_handler(DatabaseIntegrityError, database_integrity_handler)


def main():
    pass

if __name__ == "__main__":
    main()
