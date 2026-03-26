from typing import Optional

from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    author_id: int
    title: str
    published_year: int

    model_config = ConfigDict(from_attributes=True, strict=True)


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    author_id: Optional[int] = None
    title: Optional[str] = None
    published_year: Optional[int] = None


class Book(BookBase):
    id: int
