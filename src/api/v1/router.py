from fastapi import APIRouter

from . import authors, books, chapters, digests

PREFIX = "/v1"

base_router = APIRouter(prefix=PREFIX)
base_router.include_router(authors.router, tags=["Authors"])
base_router.include_router(books.router, tags=["Books"])
base_router.include_router(chapters.router, tags=["Chapters"])
base_router.include_router(digests.router, tags=["Digests"])
