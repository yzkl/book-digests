from typing import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.exceptions import EntityDoesNotExistError
from src.schemas import BookCreate, BookUpdate


async def create_book(params: BookCreate, session: AsyncSession) -> models.Book:
    db_book = models.Book(**params.model_dump())
    session.add(db_book)

    return db_book


async def find_book(id: int, session: AsyncSession) -> models.Book:
    db_book = await session.get(models.Book, id)

    if not db_book:
        logger.error(
            "Failed to fetch Book",
            extra={"operation": "find_book", "book_id": id},
        )

        raise EntityDoesNotExistError(f"Book with id={id} not found")

    return db_book


async def find_books(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[models.Book]:
    offset = (page - 1) * size
    stmt = select(models.Book).order_by(models.Book.id).offset(offset).limit(size)

    return (await session.scalars(stmt)).all()


async def update_book(
    id: int, params: BookUpdate, session: AsyncSession
) -> models.Book:
    db_book = await find_book(id, session)

    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(db_book, attr, value)

    session.add(db_book)

    return db_book


async def delete_book(id: int, session: AsyncSession) -> models.Book:
    db_book = await find_book(id, session)

    await session.delete(db_book)

    return db_book


async def count_all_books(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(models.Book)

    return await session.scalar(stmt) or 0
