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

        logger.info(
            "Chapter successfully created",
            extra={
                "operation": "create_chapter",
                "chapter_number": params.number,
                "chapter_id": db_chapter.id,
            },
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.exception(
            "Failed to create Chapter due to foreign key constraints",
            extra={
                "operation": "create_chapter",
                "chapter_number": params.number,
                "book_id": params.book_id,
            },
        )

        raise RelatedEntityDoesNotExistError(
            f"Book with id={params.book_id} not found"
        ) from exc

    return Chapter.model_validate(db_chapter)


async def get_chapter(id: int, session: AsyncSession) -> Chapter:
    db_chapter = await chapters.find_chapter(id, session)

    logger.info(
        "Chapter successfully fetched",
        extra={
            "operation": "get_chapter",
            "chapter_number": db_chapter.number,
            "chapter_id": id,
        },
    )

    return Chapter.model_validate(db_chapter)


async def get_chapters(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[Chapter]:
    db_chapters = await chapters.find_chapters(session, page, size)

    logger.info(
        "Chapters fetched",
        extra={
            "operation": "get_chapters",
            "page": page,
            "size": size,
            "count": len(db_chapters),
        },
    )

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

        logger.info(
            "Chapter successfully updated",
            extra={
                "operation": "update_chapter",
                "chapter_number": chapter_number,
                "chapter_id": id,
            },
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.exception(
            "Failed to update Chapter due to foreign key constraints",
            extra={
                "operation": "update_chapter",
                "chapter_number": chapter_number,
                "chapter_id": id,
                "book_id": book_id,
            },
        )

        raise RelatedEntityDoesNotExistError(
            f"Book with id={book_id} not found"
        ) from exc

    return Chapter.model_validate(db_chapter)


async def delete_chapter(id: int, session: AsyncSession) -> Chapter:
    db_chapter = await chapters.delete_chapter(id, session)
    chapter_number = db_chapter.number

    await session.commit()

    logger.info(
        "Chapter successfully deleted",
        extra={
            "operation": "delete_chapter",
            "chapter_number": chapter_number,
            "chapter_id": id,
            "deleted": True,
        },
    )

    return Chapter.model_validate(db_chapter)
