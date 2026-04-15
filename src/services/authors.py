from typing import Sequence

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import authors
from src.exceptions import EntityAlreadyExistsError
from src.schemas import Author, AuthorCreate, AuthorUpdate


async def create_author(params: AuthorCreate, session: AsyncSession) -> Author:
    db_author = await authors.create_author(params, session)

    try:
        await session.commit()
        await session.refresh(db_author)

        logger.bind(
            event="author_created",
            author_name=db_author.name,
            author_id=db_author.id,
        ).info("Author successfully created")

    except IntegrityError as exc:
        await session.rollback()

        logger.bind(
            code=EntityAlreadyExistsError.code,
            event="create_author",
            author_name=params.name,
        ).warning("Failed to create Author due to integrity constraints")

        raise EntityAlreadyExistsError(
            f"Author '{params.name}' already exists"
        ) from exc

    return Author.model_validate(db_author)


async def get_author(id: int, session: AsyncSession) -> Author:
    db_author = await authors.find_author(id, session)

    logger.bind(event="author_fetched", author_name=db_author.name, author_id=id).info(
        "Author successfully fetched"
    )

    return Author.model_validate(db_author)


async def get_authors(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[Author]:
    db_authors = await authors.find_authors(session, page, size)

    logger.bind(
        event="authors_listed", page=page, size=size, count=len(db_authors)
    ).info("Authors listed")

    return [Author.model_validate(d) for d in db_authors]


async def update_author(id: int, params: AuthorUpdate, session: AsyncSession) -> Author:
    db_author = await authors.update_author(id, params, session)
    author_name = db_author.name

    try:
        await session.commit()
        await session.refresh(db_author)

        logger.bind(event="author_updated", author_name=author_name, author_id=id).info(
            "Author successfully updated"
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.bind(
            code=EntityAlreadyExistsError.code,
            event="update_author",
            author_name=author_name,
            author_id=id,
        ).warning("Failed to update Author due to integrity constraints")

        raise EntityAlreadyExistsError(
            f"Author '{author_name}' already exists"
        ) from exc

    return Author.model_validate(db_author)


async def delete_author(id: int, session: AsyncSession) -> Author:
    db_author = await authors.delete_author(id, session)
    author_name = db_author.name

    await session.commit()

    logger.bind(
        event="author_deleted", author_name=author_name, author_id=id, deleted=True
    ).info("Author successfully deleted")

    return Author.model_validate(db_author)
