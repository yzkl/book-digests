from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.api.v1.router import base_router
from src.config.settings import get_settings
from src.database.session import get_db_session
from src.exceptions import BookDigestApiError
from src.exceptions.handler import book_digest_api_exception_handler
from src.models import Base

settings = get_settings()
DATABASE_URL = settings.db_url

# Setup test app
test_app = FastAPI()
test_app.include_router(base_router)
test_app.add_exception_handler(BookDigestApiError, book_digest_api_exception_handler)


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(DATABASE_URL.get_secret_value())
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def reset_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def testing_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(
    testing_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield testing_session

    test_app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        try:
            yield client
        finally:
            test_app.dependency_overrides = {}
