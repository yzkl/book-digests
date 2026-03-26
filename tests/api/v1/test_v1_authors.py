import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import models

PREFIX = "/v1/authors/"

# ---- Helpers --------------------------------------------------------------------------


async def setup(session: AsyncSession) -> None:
    x1 = models.Author(id=1, name="test-author")
    x2 = models.Author(id=2, name="some-author")
    x3 = models.Author(id=3, name="other-author")
    x4 = models.Author(id=4, name="another-author")
    x5 = models.Author(id=5, name="last-author")
    session.add_all([x1, x2, x3, x4, x5])
    await session.commit()


# ---- Tests ----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_author_returns_201(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    response = await async_client.post(PREFIX, json={"name": "test-author"})

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_author_returns_409_on_already_existing_author(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.post(PREFIX, json={"name": "test-author"})

    assert response.status_code == 409
    assert "Author 'test-author' already exists" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_author_returns_200(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.get(PREFIX + "1")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_author_returns_404_on_nonexistent_author(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.get(PREFIX + "1000")

    assert response.status_code == 404
    assert "Author with id=1000 not found" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_authors_returns_data_and_pagination(
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
async def test_get_authors_respects_page_and_size(
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
async def test_get_authors_on_out_of_range_page(
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
async def test_update_author_returns_200(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.put(PREFIX + "1", json={"name": "updated-author"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_author_returns_404_on_nonexistent_author(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.put(PREFIX + "1000", json={"name": "updated-author"})

    assert response.status_code == 404
    assert "Author with id=1000 not found" in response.json()["message"]


@pytest.mark.asyncio
async def test_update_author_returns_409_on_already_existing_author(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.put(PREFIX + "2", json={"name": "test-author"})

    assert response.status_code == 409
    assert "Author 'test-author' already exists" in response.json()["message"]


@pytest.mark.asyncio
async def test_delete_author_returns_200(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.delete(PREFIX + "1")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_author_returns_404_on_nonexistent_author(
    reset_db, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)

    response = await async_client.delete(PREFIX + "1000")

    assert response.status_code == 404
    assert "Author with id=1000 not found" in response.json()["message"]
