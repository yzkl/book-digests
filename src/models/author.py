from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Author(Base):
    __tablename__ = "dim_authors"
    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    books = relationship("Book", back_populates="author", passive_deletes=True)
