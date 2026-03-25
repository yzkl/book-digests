from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Digest(Base):
    __tablename__ = "fct_digests"

    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("dim_chapters.id", ondelete="CASCADE")
    )
    paragraph_number: Mapped[int] = mapped_column(Integer, nullable=False)
    digest: Mapped[str] = mapped_column(String(5000), nullable=False)

    chapter = relationship("Chapter", back_populates="digests")
