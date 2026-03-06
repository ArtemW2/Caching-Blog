from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from src.domain.exceptions import PostTitleError, PostDataError
from src.domain.constants import MAX_TITLE_LENGTH, MAX_TEXT_LENGTH, MIN_TEXT_LENGTH


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@dataclass
class Post:
    id: UUID
    title: str | None
    text: str
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        self._validate_title(self.title)
        self._validate_text(self.text)

    def _validate_title(self, title: str | None) -> None:
        if title:
            if len(title) > MAX_TITLE_LENGTH:
                raise PostTitleError(f"Максимальная длина заголовка публикации - {MAX_TITLE_LENGTH} символов")

            if len(title.strip()) < MIN_TEXT_LENGTH:
                raise PostTitleError(
                    "Заголовок публикации должен содержать символы помимо пробелов"
                )

    def _validate_text(self, text: str) -> None:
        if not text:
            raise PostDataError("Содержание не может быть пустым")

        if len(text) > MAX_TEXT_LENGTH:
            raise PostDataError(f"Максимальная длина содержания - {MAX_TEXT_LENGTH} символов")

        if len(text.strip()) < MIN_TEXT_LENGTH:
            raise PostDataError(
                "Cодержание публикации должно содержать символы помимо пробелов"
            )

    def update(self, title: str | None = None, text: str | None = None) -> None:
        if title is not None:
            self._validate_title(title)
            self.title = title
        if text is not None:
            self._validate_text(text)
            self.text = text

        if text or title:
            self.updated_at = utc_now()
