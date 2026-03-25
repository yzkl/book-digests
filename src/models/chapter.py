from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Chapter(Base):
    __tablename__ = "dim_chapters"

    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    book_id: Mapped[int] = mapped_column(ForeignKey("dim_books.id", ondelete="CASCADE"))
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    book = relationship("Book", back_populates="chapters")
    digests = relationship("Digest", back_populates="chapter", passive_deletes=True)
