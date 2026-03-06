from uuid import UUID

from fastapi import Depends, status
from fastapi.routing import APIRouter

from src.application.dto import CreatePostDTO, PostDTO, UpdatePostDTO
from src.application.use_cases import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetPostUseCase,
    UpdatePostUseCase,
)
from src.presentation.dependencies import (
    create_post_use_case,
    delete_post_use_case,
    get_post_use_case,
    update_post_use_case,
)
from src.presentation.schemas.requests import CreatePostSchema, UpdatePostSchema
from src.presentation.schemas.responses import PostResponseSchema


post_router = APIRouter(prefix="/posts")


@post_router.get("/{post_id}", status_code=status.HTTP_200_OK,response_model=PostResponseSchema)
async def get_post(
    post_id: UUID, use_case: GetPostUseCase = Depends(get_post_use_case)
) -> PostResponseSchema:
    dto = await use_case(post_id)

    return PostResponseSchema.from_dto(dto)


@post_router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponseSchema)
async def create_post(
    post: CreatePostSchema, use_case: CreatePostUseCase = Depends(create_post_use_case)
) -> PostResponseSchema:
    dto: CreatePostDTO = CreatePostSchema.to_dto(post)

    result_dto: PostDTO = await use_case(dto)
    return PostResponseSchema.from_dto(result_dto)


@post_router.patch("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostResponseSchema)
async def update_post(
    post_id: UUID,
    post: UpdatePostSchema,
    use_case: UpdatePostUseCase = Depends(update_post_use_case),
) -> PostResponseSchema:
    dto: UpdatePostDTO = UpdatePostSchema.to_dto(post)

    result_dto: PostDTO = await use_case(post_id, dto)

    return PostResponseSchema.from_dto(result_dto)


@post_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID, use_case: DeletePostUseCase = Depends(delete_post_use_case)
) -> None:
    await use_case(post_id)
