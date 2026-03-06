from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.application.dto import PostDTO


class PostResponseSchema(BaseModel):
    id: UUID
    title: str | None
    text: str 
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_dto(cls, dto: PostDTO) -> "PostResponseSchema":
        return PostResponseSchema(
            id=dto.id,
            title=dto.title,
            text=dto.text,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
    