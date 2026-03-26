from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src import services
from src.core.limiter import limiter
from src.crud import books
from src.database.session import get_db_session
from src.schemas import Book, BookCreate, BooksResponse, BookUpdate, Pagination

PREFIX = "/books"

router = APIRouter(prefix=PREFIX)


@router.post("/", response_model=Book, status_code=201)
@limiter.limit("60/second")
async def create_book(
    request: Request, params: BookCreate, db: AsyncSession = Depends(get_db_session)
) -> Book:
    return await services.create_book(params, db)


@router.get("/{id}", response_model=Book)
@limiter.limit("60/second")
async def get_book(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Book:
    return await services.get_book(id, db)


@router.get("/", response_model=BooksResponse)
@limiter.limit("60/second")
async def get_books(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
    size: int = Query(
        10, ge=1, description="Maximum number of results per page (must be >= 1)"
    ),
    db: AsyncSession = Depends(get_db_session),
) -> BooksResponse:
    data = await services.get_books(db, page, size)
    total = await books.count_all_books(db)
    pagination = Pagination(page=page, size=size, count=len(data), total=total)
    links = services.make_pagination_links(str(request.url), page, size, total)

    return BooksResponse(
        data=data,
        pagination=pagination,
        links=links,
    )


@router.put("/{id}", response_model=Book)
@limiter.limit("60/second")
async def update_book(
    request: Request,
    id: int,
    params: BookUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Book:
    return await services.update_book(id, params, db)


@router.delete("/{id}", response_model=Book)
@limiter.limit("60/second")
async def delete_book(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Book:
    return await services.delete_book(id, db)
