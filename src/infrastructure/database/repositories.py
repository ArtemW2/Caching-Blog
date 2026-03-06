from enum import Enum
from functools import wraps
from uuid import UUID

from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Post
from src.domain.interfaces import PostRepository
from src.infrastructure.database.models import PostModel
from src.infrastructure.exceptions import (
    DatabaseConnectionError,
    DatabaseError,
    DatabaseIntegrityError,
)
from src.infrastructure.mapper import PostModelMapper
from src.logger import get_logger

logger = get_logger(__name__)


class OperationType(Enum):
    GET = "get_by_id"
    SAVE = "save"
    UPDATE = "update"
    DELETE = "delete"


def db_operation(operation_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except IntegrityError as e:
                logger.error(
                    f"Ошибка целостности данных БД при операции {operation_name}: {e}",
                    exc_info=True,
                )
                raise DatabaseIntegrityError(e) from e
            except OperationalError as e:
                logger.error(
                    f"Ошибка БД при операции {operation_name}: {e}", exc_info=True
                )
                raise DatabaseConnectionError(operation_name, e) from e
            except SQLAlchemyError as e:
                logger.error(
                    f"Непредвиденная ошибка БД при операции {operation_name}: {e}",
                    exc_info=True,
                )
                raise DatabaseError(e=e) from e

        return wrapper

    return decorator


class SQLAlchemyPostRepository(PostRepository):
    def __init__(self, session: AsyncSession, mapper: PostModelMapper) -> None:
        self.session: AsyncSession = session
        self.mapper: PostModelMapper = mapper

    @db_operation(OperationType.GET.value)
    async def get_by_id(self, post_id: UUID) -> Post | None:
        model: PostModel | None = await self.session.get(PostModel, post_id)

        if model is None:
            return None

        return self.mapper.to_domain(model)

    @db_operation(OperationType.SAVE.value)
    async def save(self, post: Post) -> None:
        post_model = PostModel(
            id=post.id,
            title=post.title,
            text=post.text,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

        self.session.add(post_model)
        await self.session.flush()

    @db_operation(OperationType.UPDATE.value)
    async def update(self, post: Post) -> None:
        stmt = (
            update(PostModel)
            .where(PostModel.id == post.id)
            .values(
                title=post.title,
                text=post.text,
                updated_at=post.updated_at
            )
        )
        
        await self.session.execute(stmt)
        await self.session.flush()

    @db_operation(OperationType.DELETE.value)
    async def delete(self, post_id: UUID) -> bool:
        result = await self.session.execute(
            delete(PostModel).where(PostModel.id == post_id)
        )
        await self.session.flush()
        return result.rowcount > 0
