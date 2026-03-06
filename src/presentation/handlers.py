from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.application.exceptions import PostNotFoundError
from src.domain.exceptions import PostDataError, PostTitleError
from src.infrastructure.exceptions import (
    DatabaseConnectionError,
    DatabaseError,
    DatabaseIntegrityError,
)


async def post_not_found_handler(request: Request, exc: PostNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def invalid_post_content_handler(request: Request, exc: PostTitleError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": str(exc)}
    )


async def post_data_handler(request: Request, exc: PostDataError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": str(exc)}
    )


async def database_connection_handler(request: Request, exc: DatabaseConnectionError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Сервис временно недоступен. Повторите попытку через несколько секунд"
        },
    )


async def database_integrity_handler(request: Request, exc: DatabaseIntegrityError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": str(exc)}
    )


async def database_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера"},
    )
