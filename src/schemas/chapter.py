from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChapterBase(BaseModel):
    book_id: int
    number: int
    title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, strict=True)


class ChapterCreate(ChapterBase):
    pass


class ChapterUpdate(ChapterBase):
    book_id: Optional[int] = None
    number: Optional[int] = None
    title: Optional[str] = None


class Chapter(ChapterBase):
    id: int
