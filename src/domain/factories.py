from uuid import uuid4

from src.domain.entities import Post


class PostFactory:
    def create(self, title: str | None, text: str) -> Post:
        return Post(id=uuid4(), title=title, text=text)