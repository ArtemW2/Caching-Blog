from src.infrastructure.database.models import PostModel
from src.domain.entities import Post

class PostModelMapper:
    def to_domain(self, model: PostModel):
        return Post(
            id=model.id,
            title=model.title,
            text=model.text,
            created_at=model.created_at,
            updated_at=model.updated_at
        )