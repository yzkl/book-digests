import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from src import models, services
from src.exceptions import EntityDoesNotExistError, RelatedEntityDoesNotExistError
from src.schemas import Book, BookCreate, BookUpdate

# ---- Helpers --------------------------------------------------------------------------


async def setup_authors(session: AsyncSession) -> None:
    a1 = models.Author(id=1, name="test-author")
    a2 = models.Author(id=2, name="some-author")
    a3 = models.Author(id=3, name="other-author")
    a4 = models.Author(id=4, name="another-author")

    session.add_all([a1, a2, a3, a4])
    await session.commit()


async def setup(session: AsyncSession) -> dict[str, models.Book]:
    await setup_authors(session)

    x1 = models.Book(id=1, author_id=1, title="test-book", published_year=2000)
    x2 = models.Book(id=2, author_id=2, title="some-book", published_year=2001)
    x3 = models.Book(id=3, author_id=3, title="other-book", published_year=2002)
    x4 = models.Book(id=4, author_id=4, title="another-book", published_year=2003)

    all_books = {"x1": x1, "x2": x2, "x3": x3, "x4": x4}

    session.add_all(all_books.values())
    await session.commit()

    return all_books


def assert_model_equal(expected: models.Book, result: Book) -> None:
    mapper = inspect(expected.__class__)
    for column in mapper.columns:
        if column.key == "id":
            continue
        assert getattr(expected, column.key) == getattr(result, column.key)


# ---- Tests ----------------------------------------------------------------------------


# ---------------
# create_book
# ---------------
@pytest.mark.asyncio
async def test_create_book_happy_path(reset_db, testing_session: AsyncSession) -> None:
    await setup_authors(testing_session)

    result = await services.create_book(
        BookCreate(author_id=1, title="test-book", published_year=2000), testing_session
    )

    assert result.author_id == 1
    assert result.title == "test-book"
    assert result.published_year == 2000


@pytest.mark.asyncio
async def test_create_book_raises_on_nonexistent_author(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(
        RelatedEntityDoesNotExistError, match="Author with id=1000 not found"
    ):
        await services.create_book(
            BookCreate(author_id=1000, title="test-book", published_year=2000),
            testing_session,
        )


# ---------------
# get_book
# ---------------
@pytest.mark.asyncio
async def test_get_book_happy_path(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await services.get_book(1, testing_session)

    assert_model_equal(data["x1"], result)


@pytest.mark.asyncio
async def test_get_book_raises_on_nonexistent_book(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Book with id=1000 not found"):
        await services.get_book(1000, testing_session)


# ---------------
# get_books
# ---------------
@pytest.mark.asyncio
async def test_get_books_happy_path(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await services.get_books(testing_session)

    assert len(result) == 4
    assert_model_equal(data["x1"], result[0])
    assert_model_equal(data["x2"], result[1])
    assert_model_equal(data["x3"], result[2])
    assert_model_equal(data["x4"], result[3])


@pytest.mark.asyncio
async def test_get_books_ordering(reset_db, testing_session: AsyncSession) -> None:
    await setup(testing_session)

    result = await services.get_books(testing_session)
    ids = [r.id for r in result]

    assert ids == sorted(ids)


@pytest.mark.asyncio
async def test_get_books_returns_empty_sequence(
    reset_db, testing_session: AsyncSession
) -> None:
    result = await services.get_books(testing_session)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_books_custom_page(reset_db, testing_session: AsyncSession) -> None:
    await setup(testing_session)

    result = await services.get_books(testing_session, page=1000)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_books_custom_size(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await services.get_books(testing_session, size=2)

    assert len(result) == 2
    assert_model_equal(data["x1"], result[0])
    assert_model_equal(data["x2"], result[1])


@pytest.mark.asyncio
async def test_get_books_custom_page_custom_size(
    reset_db, testing_session: AsyncSession
) -> None:
    data = await setup(testing_session)

    result = await services.get_books(testing_session, page=2, size=3)

    assert len(result) == 1
    assert_model_equal(data["x4"], result[0])


# ---------------
# update_book
# ---------------
@pytest.mark.asyncio
async def test_update_book_happy_path(reset_db, testing_session: AsyncSession) -> None:
    await setup(testing_session)

    result = await services.update_book(
        1, BookUpdate(title="updated-book"), testing_session
    )

    assert result.author_id == 1
    assert result.title == "updated-book"
    assert result.published_year == 2000


@pytest.mark.asyncio
async def test_update_book_raises_on_nonexistent_book(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Book with id=1000 not found"):
        await services.update_book(
            1000, BookUpdate(name="updated-book"), testing_session
        )


@pytest.mark.asyncio
async def test_update_book_raises_on_nonexistent_author(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(
        RelatedEntityDoesNotExistError, match="Author with id=1000 not found"
    ):
        await services.update_book(1, BookUpdate(author_id=1000), testing_session)


# ---------------
# delete_book
# ---------------
@pytest.mark.asyncio
async def test_delete_book_happy_path(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await services.delete_book(1, testing_session)

    assert_model_equal(data["x1"], result)


@pytest.mark.asyncio
async def test_delete_book_raises_on_nonexistent_book(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Book with id=1000 not found"):
        await services.delete_book(1000, testing_session)
