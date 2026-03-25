from typing import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.exceptions import EntityDoesNotExistError
from src.schemas import ChapterCreate, ChapterUpdate


async def create_chapter(
    params: ChapterCreate, session: AsyncSession
) -> models.Chapter:
    db_chapter = models.Chapter(**params.model_dump())
    session.add(db_chapter)

    return db_chapter


async def find_chapter(id: int, session: AsyncSession) -> models.Chapter:
    db_chapter = await session.get(models.Chapter, id)

    if not db_chapter:
        logger.error(
            "Failed to fetch Chapter",
            extra={"operation": "find_chapter", "chapter_id": id},
        )

        raise EntityDoesNotExistError(f"Chapter with id={id} not found")

    return db_chapter


async def find_chapters(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[models.Chapter]:
    offset = (page - 1) * size
    stmt = select(models.Chapter).order_by(models.Chapter.id).offset(offset).limit(size)

    return (await session.scalars(stmt)).all()


async def update_chapter(
    id: int, params: ChapterUpdate, session: AsyncSession
) -> models.Chapter:
    db_chapter = await find_chapter(id, session)

    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(db_chapter, attr, value)

    session.add(db_chapter)

    return db_chapter


async def delete_chapter(id: int, session: AsyncSession) -> models.Chapter:
    db_chapter = await find_chapter(id, session)

    await session.delete(db_chapter)

    return db_chapter


async def count_all_chapters(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(models.Chapter)

    return await session.scalar(stmt) or 0
