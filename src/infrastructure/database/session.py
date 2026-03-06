from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)


def create_db_engine(URL) -> AsyncEngine:
    return create_async_engine(URL)


def get_session_factory(engine: AsyncEngine) -> AsyncSession:
    return async_sessionmaker(bind=engine, autocommit=False, autoflush=False)
