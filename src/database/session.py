from contextlib import asynccontextmanager
from typing import AsyncIterator

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import get_settings
from src.exceptions import ServiceError

settings = get_settings()
DATABASE_URL = settings.db_url


class DatabaseSessionManager:
    def __init__(self, host: str, **engine_kwargs):
        try:
            self.engine: AsyncEngine | None = create_async_engine(host, **engine_kwargs)
            self._sessionmaker: async_sessionmaker[AsyncSession] | None = (
                async_sessionmaker(bind=self.engine, expire_on_commit=False)
            )

        except SQLAlchemyError:
            logger.exception("Failed to initialize database engine.")
            raise ServiceError

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
            logger.info("Database engine disposed.")
            self.engine = None
            self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            logger.error("Attempted to connect but engine is not initialized.")
            raise ServiceError

        logger.debug("Opening database connection.")
        async with self.engine.begin() as connection:
            try:
                yield connection

            except SQLAlchemyError:
                await connection.rollback()
                logger.exception("Database transaction failed during connection block.")
                raise ServiceError

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            logger.error("Sessionmaker is unavailable.")
            raise ServiceError

        logger.debug("Opening database session.")
        session = self._sessionmaker()

        try:
            yield session

        except SQLAlchemyError:
            await session.rollback()
            logger.exception("Database session failed.")
            raise ServiceError

        finally:
            await session.close()
            logger.debug("Database session closed.")


sessionmanager = DatabaseSessionManager(DATABASE_URL.get_secret_value())


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with sessionmanager.session() as session:
        yield session
