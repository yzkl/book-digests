from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src import services
from src.core.limiter import limiter
from src.crud import authors
from src.database.session import get_db_session
from src.schemas import Author, AuthorCreate, AuthorsResponse, AuthorUpdate, Pagination

PREFIX = "/authors"

router = APIRouter(prefix=PREFIX)


@router.post("/", response_model=Author, status_code=201)
@limiter.limit("60/second")
async def create_author(
    request: Request, params: AuthorCreate, db: AsyncSession = Depends(get_db_session)
) -> Author:
    return await services.create_author(params, db)


@router.get("/{id}", response_model=Author)
@limiter.limit("60/second")
async def get_author(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Author:
    return await services.get_author(id, db)


@router.get("/", response_model=AuthorsResponse)
@limiter.limit("60/second")
async def get_authors(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
    size: int = Query(
        10, ge=1, description="Maximum number of results per page (must be >= 1)"
    ),
    db: AsyncSession = Depends(get_db_session),
) -> AuthorsResponse:
    data = await services.get_authors(db, page, size)
    total = await authors.count_all_authors(db)
    pagination = Pagination(page=page, size=size, count=len(data), total=total)
    links = services.make_pagination_links(str(request.url), page, size, total)

    return AuthorsResponse(
        data=data,
        pagination=pagination,
        links=links,
    )


@router.put("/{id}", response_model=Author)
@limiter.limit("60/second")
async def update_author(
    request: Request,
    id: int,
    params: AuthorUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Author:
    return await services.update_author(id, params, db)


@router.delete("/{id}", response_model=Author)
@limiter.limit("60/second")
async def delete_author(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Author:
    return await services.delete_author(id, db)
