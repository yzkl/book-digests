from typing import Sequence

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import digests
from src.exceptions import RelatedEntityDoesNotExistError
from src.schemas import Digest, DigestCreate, DigestUpdate


async def create_digest(params: DigestCreate, session: AsyncSession) -> Digest:
    db_digest = await digests.create_digest(params, session)

    try:
        await session.commit()
        await session.refresh(db_digest)

        logger.bind(event="digest_created", digest_id=db_digest.id).info(
            "Digest successfully created"
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.bind(
            code=RelatedEntityDoesNotExistError.code,
            event="create_digest",
            chapter_id=params.chapter_id,
        ).warning("Failed to create Digest due to foreign key constraints")

        raise RelatedEntityDoesNotExistError(
            f"Chapter with id={params.chapter_id} not found"
        ) from exc

    return Digest.model_validate(db_digest)


async def get_digest(id: int, session: AsyncSession) -> Digest:
    db_digest = await digests.find_digest(id, session)

    logger.bind(event="digest_fetched", digest_id=id).info(
        "Digest successfully fetched"
    )

    return Digest.model_validate(db_digest)


async def get_digests(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[Digest]:
    db_digests = await digests.find_digests(session, page, size)

    logger.bind(
        event="digests_listed", page=page, size=size, count=len(db_digests)
    ).info("Digests listed")

    return [Digest.model_validate(d) for d in db_digests]


async def update_digest(id: int, params: DigestUpdate, session: AsyncSession) -> Digest:
    db_digest = await digests.update_digest(id, params, session)
    chapter_id = db_digest.chapter_id

    try:
        await session.commit()
        await session.refresh(db_digest)

        logger.bind(event="digest_updated", digest_id=id).info(
            "Digest successfully updated"
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.bind(
            code=RelatedEntityDoesNotExistError.code,
            event="update_digest",
            digest_id=id,
            chapter_id=chapter_id,
        ).warning("Failed to update Digest due to foreign key constraints")

        raise RelatedEntityDoesNotExistError(
            f"Chapter with id={chapter_id} not found"
        ) from exc

    return Digest.model_validate(db_digest)


async def delete_digest(id: int, session: AsyncSession) -> Digest:
    db_digest = await digests.delete_digest(id, session)

    await session.commit()

    logger.bind(event="digest_deleted", digest_id=id, deleted=True).info(
        "Digest successfully deleted",
    )

    return Digest.model_validate(db_digest)
