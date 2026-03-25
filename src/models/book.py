from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Book(Base):
    __tablename__ = "dim_books"

    id: Mapped[Optional[str]] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("dim_authors.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    published_year: Mapped[int] = mapped_column(Integer, nullable=False)

    author = relationship("Author", back_populates="books")
    chapters = relationship("Chapter", back_populates="book", passive_deletes=True)
