from typing import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.exceptions import EntityDoesNotExistError
from src.schemas import AuthorCreate, AuthorUpdate


async def create_author(params: AuthorCreate, session: AsyncSession) -> models.Author:
    db_author = models.Author(**params.model_dump())
    session.add(db_author)

    return db_author


async def find_author(id: int, session: AsyncSession) -> models.Author:
    db_author = await session.get(models.Author, id)

    if not db_author:
        logger.bind(
            code=EntityDoesNotExistError.code, event="find_author", author_id=id
        ).warning("Author not found")

        raise EntityDoesNotExistError(f"Author with id={id} not found")

    return db_author


async def find_authors(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[models.Author]:
    offset = (page - 1) * size
    stmt = select(models.Author).order_by(models.Author.id).offset(offset).limit(size)

    return (await session.scalars(stmt)).all()


async def update_author(
    id: int, params: AuthorUpdate, session: AsyncSession
) -> models.Author:
    db_author = await find_author(id, session)

    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(db_author, attr, value)

    session.add(db_author)

    return db_author


async def delete_author(id: int, session: AsyncSession) -> models.Author:
    db_author = await find_author(id, session)

    await session.delete(db_author)

    return db_author


async def count_all_authors(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(models.Author)

    return await session.scalar(stmt) or 0
