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

        logger.info(
            "Digest successfully created",
            extra={
                "operation": "create_digest",
                "digest": params.digest,
                "digest_id": db_digest.id,
            },
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.exception(
            "Failed to create Digest due to foreign key constraints",
            extra={
                "operation": "create_digest",
                "digest": params.digest,
                "chapter_id": params.chapter_id,
            },
        )

        raise RelatedEntityDoesNotExistError(
            f"Chapter with id={params.chapter_id} not found"
        ) from exc

    return Digest.model_validate(db_digest)


async def get_digest(id: int, session: AsyncSession) -> Digest:
    db_digest = await digests.find_digest(id, session)

    logger.info(
        "Digest successfully fetched",
        extra={
            "operation": "get_digest",
            "digest": db_digest.digest,
            "digest_id": id,
        },
    )

    return Digest.model_validate(db_digest)


async def get_digests(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[Digest]:
    db_digests = await digests.find_digests(session, page, size)

    logger.info(
        "Digests fetched",
        extra={
            "operation": "get_digests",
            "page": page,
            "size": size,
            "count": len(db_digests),
        },
    )

    return [Digest.model_validate(d) for d in db_digests]


async def update_digest(id: int, params: DigestUpdate, session: AsyncSession) -> Digest:
    db_digest = await digests.update_digest(id, params, session)
    digest = db_digest.digest
    chapter_id = db_digest.chapter_id

    try:
        await session.commit()
        await session.refresh(db_digest)

        logger.info(
            "Digest successfully updated",
            extra={
                "operation": "update_digest",
                "digest": digest,
                "digest_id": id,
            },
        )

    except IntegrityError as exc:
        await session.rollback()

        logger.exception(
            "Failed to update Digest due to foreign key constraints",
            extra={
                "operation": "update_digest",
                "digest": digest,
                "digest_id": id,
                "chapter_id": chapter_id,
            },
        )

        raise RelatedEntityDoesNotExistError(
            f"Chapter with id={chapter_id} not found"
        ) from exc

    return Digest.model_validate(db_digest)


async def delete_digest(id: int, session: AsyncSession) -> Digest:
    db_digest = await digests.delete_digest(id, session)
    digest = db_digest.digest

    await session.commit()

    logger.info(
        "Digest successfully deleted",
        extra={
            "operation": "delete_digest",
            "digest": digest,
            "digest_id": id,
            "deleted": True,
        },
    )

    return Digest.model_validate(db_digest)
