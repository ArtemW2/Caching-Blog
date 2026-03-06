from src.domain.entities import Post
from src.application.dto import PostDTO
from datetime import datetime
from uuid import UUID

class PostMapper:
    def to_entity(self, dto: PostDTO) -> Post:
        return Post(
            id=dto.id,
            title=dto.title,
            text=dto.text,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
    
    def to_dto(self, post: Post) -> PostDTO:
        return PostDTO(
            id=post.id,
            title=post.title,
            text=post.text,
            created_at=post.created_at,
            updated_at=post.updated_at   
        )
    
    def dict_to_dto(self, post_dict: dict) -> PostDTO:
        return PostDTO(
            id=UUID(post_dict["id"]),
            title=post_dict["title"],
            text=post_dict["text"],
            created_at=post_dict["created_at"],
            updated_at=post_dict["updated_at"] if post_dict.get("updated_at") else None
        )
    
    def to_dict(self, post: Post) -> dict:
        return {
            "id": str(post.id),
            "title": post.title,
            "text": post.text,
            "created_at": datetime.isoformat(post.created_at),
            "updated_at": datetime.isoformat(post.updated_at) if post.updated_at else None
        }
    
