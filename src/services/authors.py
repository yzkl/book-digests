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

        logger.info(
            "Author successfully created",
            extra={
                "operation": "create_author",
                "author_name": db_author.name,
                "author_id": db_author.id,
            },
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.exception(
            "Failed to create Author due to integrity constraints",
            extra={
                "operation": "create_author",
                "author_name": params.name,
            },
        )

        raise EntityAlreadyExistsError(
            f"Author '{params.name}' already exists"
        ) from exc

    return Author.model_validate(db_author)


async def get_author(id: int, session: AsyncSession) -> Author:
    db_author = await authors.find_author(id, session)

    logger.info(
        "Author successfully fetched",
        extra={
            "operation": "get_author",
            "author_name": db_author.name,
            "author_id": id,
        },
    )

    return Author.model_validate(db_author)


async def get_authors(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[Author]:
    db_authors = await authors.find_authors(session, page, size)

    logger.info(
        "Authors fetched",
        extra={
            "operation": "get_authors",
            "page": page,
            "size": size,
            "count": len(db_authors),
        },
    )

    return [Author.model_validate(d) for d in db_authors]


async def update_author(id: int, params: AuthorUpdate, session: AsyncSession) -> Author:
    db_author = await authors.update_author(id, params, session)
    author_name = db_author.name

    try:
        await session.commit()
        await session.refresh(db_author)

        logger.info(
            "Author successfully updated",
            extra={
                "operation": "update_author",
                "author_name": author_name,
                "author_id": id,
            },
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.exception(
            "Failed to update Author due to integrity constraints",
            extra={
                "operation": "update_author",
                "author_name": author_name,
                "author_id": id,
            },
        )

        raise EntityAlreadyExistsError(
            f"Author '{author_name}' already exists"
        ) from exc

    return Author.model_validate(db_author)


async def delete_author(id: int, session: AsyncSession) -> Author:
    db_author = await authors.delete_author(id, session)
    author_name = db_author.name

    await session.commit()

    logger.info(
        "Author successfully deleted",
        extra={
            "operation": "delete_author",
            "author_name": author_name,
            "author_id": id,
            "deleted": True,
        },
    )

    return Author.model_validate(db_author)
