from typing import Sequence

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import chapters
from src.exceptions import RelatedEntityDoesNotExistError
from src.schemas import Chapter, ChapterCreate, ChapterUpdate


async def create_chapter(params: ChapterCreate, session: AsyncSession) -> Chapter:
    db_chapter = await chapters.create_chapter(params, session)

    try:
        await session.commit()
        await session.refresh(db_chapter)

        logger.bind(
            event="chapter_created",
            chapter_number=params.number,
            chapter_id=db_chapter.id,
        ).info("Chapter successfully created")

    except IntegrityError as exc:
        await session.rollback()

        logger.bind(
            code=RelatedEntityDoesNotExistError.code,
            event="create_chapter",
            chapter_number=params.number,
            book_id=params.book_id,
        ).warning("Failed to create Chapter due to foreign key constraints")

        raise RelatedEntityDoesNotExistError(
            f"Book with id={params.book_id} not found"
        ) from exc

    return Chapter.model_validate(db_chapter)


async def get_chapter(id: int, session: AsyncSession) -> Chapter:
    db_chapter = await chapters.find_chapter(id, session)

    logger.bind(
        event="chapter_fetched", chapter_number=db_chapter.number, chapter_id=id
    ).info("Chapter successfully fetched")

    return Chapter.model_validate(db_chapter)


async def get_chapters(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[Chapter]:
    db_chapters = await chapters.find_chapters(session, page, size)

    logger.bind(
        event="chapters_listed", page=page, size=size, count=len(db_chapters)
    ).info("Chapters listed")

    return [Chapter.model_validate(d) for d in db_chapters]


async def update_chapter(
    id: int, params: ChapterUpdate, session: AsyncSession
) -> Chapter:
    db_chapter = await chapters.update_chapter(id, params, session)
    chapter_number = db_chapter.number
    book_id = db_chapter.book_id

    try:
        await session.commit()
        await session.refresh(db_chapter)

        logger.bind(
            event="chapter_updated", chapter_number=chapter_number, chapter_id=id
        ).info("Chapter successfully updated")

    except IntegrityError as exc:
        await session.rollback()

        logger.bind(
            code=RelatedEntityDoesNotExistError.code,
            event="update_chapter",
            chapter_number=chapter_number,
            chapter_id=id,
            book_id=book_id,
        ).warning("Failed to update Chapter due to foreign key constraints")

        raise RelatedEntityDoesNotExistError(
            f"Book with id={book_id} not found"
        ) from exc

    return Chapter.model_validate(db_chapter)


async def delete_chapter(id: int, session: AsyncSession) -> Chapter:
    db_chapter = await chapters.delete_chapter(id, session)
    chapter_number = db_chapter.number

    await session.commit()

    logger.bind(
        event="chapter_deleted",
        chapter_number=chapter_number,
        chapter_id=id,
        deleted=True,
    ).info("Chapter successfully deleted")

    return Chapter.model_validate(db_chapter)
