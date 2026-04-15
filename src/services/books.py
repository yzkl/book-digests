from typing import Sequence

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import books
from src.exceptions import RelatedEntityDoesNotExistError
from src.schemas import Book, BookCreate, BookUpdate


async def create_book(params: BookCreate, session: AsyncSession) -> Book:
    db_book = await books.create_book(params, session)

    try:
        await session.commit()
        await session.refresh(db_book)

        logger.bind(
            event="book_created", book_title=params.title, book_id=db_book.id
        ).info("Book successfully created")

    except IntegrityError as exc:
        await session.rollback()

        logger.bind(
            code=RelatedEntityDoesNotExistError.code,
            event="create_book",
            book_title=params.title,
            author_id=params.author_id,
        ).warning("Failed to create Book due to foreign key constraints")

        raise RelatedEntityDoesNotExistError(
            f"Author with id={params.author_id} not found"
        ) from exc

    return Book.model_validate(db_book)


async def get_book(id: int, session: AsyncSession) -> Book:
    db_book = await books.find_book(id, session)

    logger.bind(event="book_fetched", book_title=db_book.title, book_id=id).info(
        "Book successfully fetched"
    )

    return Book.model_validate(db_book)


async def get_books(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[Book]:
    db_books = await books.find_books(session, page, size)

    logger.bind(event="books_listed", page=page, size=size, count=len(db_books)).info(
        "Books listed"
    )

    return [Book.model_validate(d) for d in db_books]


async def update_book(id: int, params: BookUpdate, session: AsyncSession) -> Book:
    db_book = await books.update_book(id, params, session)
    book_title = db_book.title
    author_id = db_book.author_id

    try:
        await session.commit()
        await session.refresh(db_book)

        logger.bind(event="book_updated", book_title=book_title, book_id=id).info(
            "Book successfully updated"
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.bind(
            code=RelatedEntityDoesNotExistError.code,
            event="update_book",
            book_title=book_title,
            book_id=id,
            author_id=author_id,
        ).warning("Failed to update Book due to foreign key constraints")

        raise RelatedEntityDoesNotExistError(
            f"Author with id={author_id} not found"
        ) from exc

    return Book.model_validate(db_book)


async def delete_book(id: int, session: AsyncSession) -> Book:
    db_book = await books.delete_book(id, session)
    book_title = db_book.title

    await session.commit()

    logger.bind(
        event="book_deleted", book_title=book_title, book_id=id, deleted=True
    ).info("Book successfully deleted")

    return Book.model_validate(db_book)
