import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from src import models, services
from src.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from src.schemas import Author, AuthorCreate, AuthorUpdate

# ---- Helpers --------------------------------------------------------------------------


async def setup(session: AsyncSession) -> dict[str, models.Author]:
    x1 = models.Author(id=1, name="test-author")
    x2 = models.Author(id=2, name="some-author")
    x3 = models.Author(id=3, name="other-author")
    x4 = models.Author(id=4, name="another-author")

    all_authors = {"x1": x1, "x2": x2, "x3": x3, "x4": x4}

    session.add_all(all_authors.values())
    await session.commit()

    return all_authors


def assert_model_equal(expected: models.Author, result: Author) -> None:
    mapper = inspect(expected.__class__)
    for column in mapper.columns:
        if column.key == "id":
            continue
        assert getattr(expected, column.key) == getattr(result, column.key)


# ---- Tests ----------------------------------------------------------------------------


# -----------------
# create_author
# -----------------
@pytest.mark.asyncio
async def test_create_author_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    result = await services.create_author(
        AuthorCreate(name="test-author"), testing_session
    )

    assert result.name == "test-author"


@pytest.mark.asyncio
async def test_create_author_raises_on_already_existing_author(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(
        EntityAlreadyExistsError, match="Author 'test-author' already exists"
    ):
        await services.create_author(AuthorCreate(name="test-author"), testing_session)


# -----------------
# get_author
# -----------------
@pytest.mark.asyncio
async def test_get_author_happy_path(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await services.get_author(1, testing_session)

    assert_model_equal(data["x1"], result)


@pytest.mark.asyncio
async def test_get_author_raises_on_nonexistent_author(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Author with id=1000 not found"):
        await services.get_author(1000, testing_session)


# -----------------
# get_authors
# -----------------
@pytest.mark.asyncio
async def test_get_authors_happy_path(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await services.get_authors(testing_session)

    assert len(result) == 4
    assert_model_equal(data["x1"], result[0])
    assert_model_equal(data["x2"], result[1])
    assert_model_equal(data["x3"], result[2])
    assert_model_equal(data["x4"], result[3])


@pytest.mark.asyncio
async def test_get_authors_ordering(reset_db, testing_session: AsyncSession) -> None:
    await setup(testing_session)

    result = await services.get_authors(testing_session)
    ids = [r.id for r in result]

    assert ids == sorted(ids)


@pytest.mark.asyncio
async def test_get_authors_returns_empty_sequence(
    reset_db, testing_session: AsyncSession
) -> None:
    result = await services.get_authors(testing_session)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_authors_custom_page(reset_db, testing_session: AsyncSession) -> None:
    await setup(testing_session)

    result = await services.get_authors(testing_session, page=1000)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_authors_custom_size(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await services.get_authors(testing_session, size=2)

    assert len(result) == 2
    assert_model_equal(data["x1"], result[0])
    assert_model_equal(data["x2"], result[1])


@pytest.mark.asyncio
async def test_get_authors_custom_page_custom_size(
    reset_db, testing_session: AsyncSession
) -> None:
    data = await setup(testing_session)

    result = await services.get_authors(testing_session, page=2, size=3)

    assert len(result) == 1
    assert_model_equal(data["x4"], result[0])


# -----------------
# update_author
# -----------------
@pytest.mark.asyncio
async def test_update_author_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    result = await services.update_author(
        1, AuthorUpdate(name="updated-author"), testing_session
    )

    assert result.name == "updated-author"


@pytest.mark.asyncio
async def test_update_author_raises_on_nonexistent_author(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Author with id=1000 not found"):
        await services.update_author(
            1000, AuthorUpdate(name="updated-author"), testing_session
        )


@pytest.mark.asyncio
async def test_update_author_raises_on_already_existing_author(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(
        EntityAlreadyExistsError, match="Author 'test-author' already exists"
    ):
        await services.update_author(
            3, AuthorUpdate(name="test-author"), testing_session
        )


# -----------------
# delete_author
# -----------------
@pytest.mark.asyncio
async def test_delete_author_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    data = await setup(testing_session)

    result = await services.delete_author(1, testing_session)

    assert_model_equal(data["x1"], result)


@pytest.mark.asyncio
async def test_delete_author_raises_on_nonexistent_author(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Author with id=1000 not found"):
        await services.delete_author(1000, testing_session)
