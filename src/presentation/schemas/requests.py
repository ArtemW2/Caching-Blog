from pydantic import BaseModel, Field

from src.application.dto import CreatePostDTO, UpdatePostDTO

class CreatePostSchema(BaseModel):
    title: str | None = Field(
        None,
        description="Заголовок публикации (максимум 50 символов)",
        example="Мой первый пост",
        max_length=50
    )
    text: str = Field(
        ...,
        description="Текст публикации (обязательно, максимум 1000 символов)",
        example="Содержание поста...",
        max_length=1000,
        min_length=1
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Пример заголовка",
                    "text": "Пример текста публикации"
                }
            ]
        }
    }

    def to_dto(self) -> CreatePostDTO:
        return CreatePostDTO(
            title=self.title,
            text=self.text
        )


class UpdatePostSchema(BaseModel):
    title: str | None = Field(
        None,
        description="Новый заголовок (максимум 50 символов)",
        example="Обновлённый заголовок",
        max_length=50
    )
    text: str | None = Field(
        None,
        description="Новый текст (максимум 1000 символов)",
        example="Обновлённое содержание...",
        max_length=1000,
        min_length=1
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Обновлённый заголовок",
                    "text": "Обновлённый текст"
                }
            ]
        }
    }

    def to_dto(self) -> UpdatePostDTO:
        return UpdatePostDTO(title=self.title, text=self.text)