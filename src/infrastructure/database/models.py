from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID
from sqlalchemy import UUID as PG_UUID, String, Text, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass


class PostModel(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(PG_UUID(True), primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(String(50), nullable=True)
    text: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), index=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
