from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src import services
from src.core.limiter import limiter
from src.crud import digests
from src.database.session import get_db_session
from src.schemas import Digest, DigestCreate, DigestsResponse, DigestUpdate, Pagination

PREFIX = "/digests"

router = APIRouter(prefix=PREFIX)


@router.post("/", response_model=Digest, status_code=status.HTTP_201_CREATED)
@limiter.limit("60/second")
async def create_digest(
    request: Request, params: DigestCreate, db: AsyncSession = Depends(get_db_session)
) -> Digest:
    return await services.create_digest(params, db)


@router.get("/{id}", response_model=Digest)
@limiter.limit("60/second")
async def get_digest(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Digest:
    return await services.get_digest(id, db)


@router.get("/", response_model=DigestsResponse)
@limiter.limit("60/second")
async def get_digests(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
    size: int = Query(
        10, ge=1, description="Maximum number of results per page (must be >= 1)"
    ),
    db: AsyncSession = Depends(get_db_session),
) -> DigestsResponse:
    data = await services.get_digests(db, page, size)
    total = await digests.count_all_digests(db)
    pagination = Pagination(page=page, size=size, count=len(data), total=total)
    links = services.make_pagination_links(str(request.url), page, size, total)

    return DigestsResponse(
        data=data,
        pagination=pagination,
        links=links,
    )


@router.put("/{id}", response_model=Digest)
@limiter.limit("60/second")
async def update_digest(
    request: Request,
    id: int,
    params: DigestUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Digest:
    return await services.update_digest(id, params, db)


@router.delete("/{id}", response_model=Digest)
@limiter.limit("60/second")
async def delete_digest(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Digest:
    return await services.delete_digest(id, db)
