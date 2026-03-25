from math import ceil
from typing import Annotated, Generic, TypeVar

from pydantic import AfterValidator, BaseModel, model_validator

from . import Author, Book, Chapter, Digest


def is_positive(value: int) -> int:
    if value <= 0:
        raise ValueError("Must be a positive number")
    return value


def is_non_negative(value: int) -> int:
    if value < 0:
        raise ValueError("Must be a non-negative number")
    return value


PositiveInt = Annotated[int, AfterValidator(is_positive)]
NonNegativeInt = Annotated[int, AfterValidator(is_non_negative)]


class Pagination(BaseModel):
    page: PositiveInt
    size: PositiveInt
    count: NonNegativeInt
    total: NonNegativeInt
    total_pages: NonNegativeInt | None = None

    @model_validator(mode="after")
    def compute_pages(self):
        self.total_pages = 0 if self.total is None else ceil(self.total / self.size)

        return self


class Links(BaseModel):
    prev: str | None = None
    next: str | None = None


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: Pagination
    links: Links


AuthorsResponse = PaginatedResponse[Author]
BooksResponse = PaginatedResponse[Book]
ChaptersResponse = PaginatedResponse[Chapter]
DigestsResponse = PaginatedResponse[Digest]
