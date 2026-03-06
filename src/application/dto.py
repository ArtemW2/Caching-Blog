from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class CreatePostDTO:
    title: str | None
    text: str


@dataclass
class UpdatePostDTO:
    title: str | None 
    text: str | None 


@dataclass
class PostDTO:
    id: UUID
    title: str | None
    text: str
    created_at: datetime
    updated_at: datetime | None 