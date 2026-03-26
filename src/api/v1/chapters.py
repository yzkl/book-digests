from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src import services
from src.core.limiter import limiter
from src.crud import chapters
from src.database.session import get_db_session
from src.schemas import (
    Chapter,
    ChapterCreate,
    ChaptersResponse,
    ChapterUpdate,
    Pagination,
)

PREFIX = "/chapters"

router = APIRouter(prefix=PREFIX)


@router.post("/", response_model=Chapter, status_code=201)
@limiter.limit("60/second")
async def create_chapter(
    request: Request, params: ChapterCreate, db: AsyncSession = Depends(get_db_session)
) -> Chapter:
    return await services.create_chapter(params, db)


@router.get("/{id}", response_model=Chapter)
@limiter.limit("60/second")
async def get_chapter(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Chapter:
    return await services.get_chapter(id, db)


@router.get("/", response_model=ChaptersResponse)
@limiter.limit("60/second")
async def get_chapters(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
    size: int = Query(
        10, ge=1, description="Maximum number of results per page (must be >= 1)"
    ),
    db: AsyncSession = Depends(get_db_session),
) -> ChaptersResponse:
    data = await services.get_chapters(db, page, size)
    total = await chapters.count_all_chapters(db)
    pagination = Pagination(page=page, size=size, count=len(data), total=total)
    links = services.make_pagination_links(str(request.url), page, size, total)

    return ChaptersResponse(
        data=data,
        pagination=pagination,
        links=links,
    )


@router.put("/{id}", response_model=Chapter)
@limiter.limit("60/second")
async def update_chapter(
    request: Request,
    id: int,
    params: ChapterUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Chapter:
    return await services.update_chapter(id, params, db)


@router.delete("/{id}", response_model=Chapter)
@limiter.limit("60/second")
async def delete_chapter(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Chapter:
    return await services.delete_chapter(id, db)
