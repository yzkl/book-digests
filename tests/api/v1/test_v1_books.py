import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import models

PREFIX = "/v1/books/"

# ---- Helpers --------------------------------------------------------------------------


async def setup_authors(session: AsyncSession) -> None:
    x1 = models.Author(id=1, name="test-author")
    x2 = models.Author(id=2, name="some-author")
    x3 = models.Author(id=3, name="other-author")
    x4 = models.Author(id=4, name="another-author")
    x5 = models.Author(id=5, name="last-author")
    session.add_all([x1, x2, x3, x4, x5])
    await session.commit()


async def setup(session: AsyncSession) -> None:
    await setup_authors(session)

    x1 = models.Book(id=1, author_id=1, title="test-book", published_year=2000)
    x2 = models.Book(id=2, author_id=2, title="some-book", published_year=2001)
    x3 = models.Book(id=3, author_id=3, title="other-book", published_year=2002)
    x4 = models.Book(id=4, author_id=4, title="another-book", published_year=2003)
    x5 = models.Book(id=5, author_id=5, title="last-book", published_year=2004)
    session.add_all([x1, x2, x3, x4, x5])
    await session.commit()


# ---- Tests ----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_book_returns_201(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_authors(testing_session)

    response = await async_client.post(
        PREFIX, json={"author_id": 1, "title": "test-book", "published_year": 2000}
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_book_returns_422_on_nonexistent_author(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.post(
        PREFIX, json={"author_id": 1000, "title": "test-book", "published_year": 2000}
    )

    assert response.status_code == 422
    assert "Author with id=1000 not found" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_book_returns_200(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.get(PREFIX + "1")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_book_returns_404_on_nonexistent_book(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.get(PREFIX + "1000")

    assert response.status_code == 404
    assert "Book with id=1000 not found" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_books_returns_data_and_pagination(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.get(PREFIX)
    body = response.json()

    assert response.status_code == 200

    # Data
    assert len(body["data"]) == 5

    # Pagination
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["size"] == 10
    assert body["pagination"]["count"] == 5
    assert body["pagination"]["total"] == 5
    assert body["pagination"]["total_pages"] == 1

    # Links
    assert body["links"]["prev"] is None
    assert body["links"]["next"] is None


@pytest.mark.asyncio
async def test_get_books_respects_page_and_size(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.get(PREFIX + "?page=2&size=2")
    body = response.json()

    assert response.status_code == 200

    # Data
    assert len(body["data"]) == 2

    # Pagination
    assert body["pagination"]["page"] == 2
    assert body["pagination"]["size"] == 2
    assert body["pagination"]["count"] == 2
    assert body["pagination"]["total"] == 5
    assert body["pagination"]["total_pages"] == 3

    # Links
    assert "page=1" in body["links"]["prev"]
    assert "page=3" in body["links"]["next"]


@pytest.mark.asyncio
async def test_get_books_on_out_of_range_page(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.get(PREFIX + "?page=1000")
    body = response.json()

    assert response.status_code == 200

    # Data
    assert len(body["data"]) == 0

    # Pagination
    assert body["pagination"]["page"] == 1000
    assert body["pagination"]["size"] == 10
    assert body["pagination"]["count"] == 0
    assert body["pagination"]["total"] == 5
    assert body["pagination"]["total_pages"] == 1

    # Links
    assert "page=999" in body["links"]["prev"]
    assert body["links"]["next"] is None


@pytest.mark.asyncio
async def test_update_book_returns_200(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.put(PREFIX + "1", json={"title": "updated-book"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_book_returns_404_on_nonexistent_book(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.put(PREFIX + "1000", json={"title": "updated-book"})

    assert response.status_code == 404
    assert "Book with id=1000 not found" in response.json()["message"]


@pytest.mark.asyncio
async def test_update_book_returns_422_on_nonexistent_author(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.put(
        PREFIX + "1", json={"author_id": 1000, "name": "updated-book"}
    )

    assert response.status_code == 422
    assert "Author with id=1000 not found" in response.json()["message"]


@pytest.mark.asyncio
async def test_delete_book_returns_200(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.delete(PREFIX + "1")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_book_returns_404_on_nonexistent_book(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.delete(PREFIX + "1000")

    assert response.status_code == 404
    assert "Book with id=1000 not found" in response.json()["message"]
