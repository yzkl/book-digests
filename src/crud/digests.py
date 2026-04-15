from typing import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.exceptions import EntityDoesNotExistError
from src.schemas import DigestCreate, DigestUpdate


async def create_digest(params: DigestCreate, session: AsyncSession) -> models.Digest:
    db_digest = models.Digest(**params.model_dump())
    session.add(db_digest)

    return db_digest


async def find_digest(id: int, session: AsyncSession) -> models.Digest:
    db_digest = await session.get(models.Digest, id)

    if not db_digest:
        logger.bind(
            code=EntityDoesNotExistError.code, event="find_digest", digest_id=id
        ).warning("Failed to fetch Digest")

        raise EntityDoesNotExistError(f"Digest with id={id} not found")

    return db_digest


async def find_digests(
    session: AsyncSession, page: int = 1, size: int = 10
) -> Sequence[models.Digest]:
    offset = (page - 1) * size
    stmt = select(models.Digest).order_by(models.Digest.id).offset(offset).limit(size)

    return (await session.scalars(stmt)).all()


async def update_digest(
    id: int, params: DigestUpdate, session: AsyncSession
) -> models.Digest:
    db_digest = await find_digest(id, session)

    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(db_digest, attr, value)

    session.add(db_digest)

    return db_digest


async def delete_digest(id: int, session: AsyncSession) -> models.Digest:
    db_digest = await find_digest(id, session)

    await session.delete(db_digest)

    return db_digest


async def count_all_digests(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(models.Digest)

    return await session.scalar(stmt) or 0
