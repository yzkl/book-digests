from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from loguru import logger

from src.api.v1.router import base_router
from src.config.settings import get_settings
from src.core.log import setup_logging
from src.database.session import sessionmanager
from src.exceptions import BookDigestApiError
from src.exceptions.handler import book_digest_api_exception_handler

settings = get_settings()

setup_logging(settings)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

    if sessionmanager.engine is not None:
        await sessionmanager.close()


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
)
app.include_router(base_router, prefix=settings.api_prefix)
app.add_exception_handler(BookDigestApiError, book_digest_api_exception_handler)


@app.get("/")
async def root(request: Request) -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok", "version": settings.version, "env": settings.env}
