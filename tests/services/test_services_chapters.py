import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from src import models, services
from src.exceptions import EntityDoesNotExistError, RelatedEntityDoesNotExistError
from src.schemas import Chapter, ChapterCreate, ChapterUpdate

# ---- Helpers --------------------------------------------------------------------------


async def setup_authors(session: AsyncSession) -> None:
    a1 = models.Author(id=1, name="test-author")
    a2 = models.Author(id=2, name="some-author")
    a3 = models.Author(id=3, name="other-author")
    a4 = models.Author(id=4, name="another-author")

    session.add_all([a1, a2, a3, a4])
    await session.commit()


async def setup_books(session: AsyncSession) -> None:
    await setup_authors(session)

    b1 = models.Book(id=1, author_id=1, title="test-book", published_year=2000)
    b2 = models.Book(id=2, author_id=2, title="some-book", published_year=2001)
    b3 = models.Book(id=3, author_id=3, title="other-book", published_year=2002)
    b4 = models.Book(id=4, author_id=4, title="another-book", published_year=2003)

    session.add_all([b1, b2, b3, b4])
    await session.commit()


async def setup(session: AsyncSession) -> dict[str, models.Chapter]:
    await setup_books(session)

    x1 = models.Chapter(id=1, book_id=1, number=1, title="test-chapter")
    x2 = models.Chapter(id=2, book_id=2, number=1)
    x3 = models.Chapter(id=3, book_id=3, number=1, title="other-chapter")
    x4 = models.Chapter(id=4, book_id=4, number=1)

    all_chapters = {"x1": x1, "x2": x2, "x3": x3, "x4": x4}

    session.add_all(all_chapters.values())
    await session.commit()

    return all_chapters


def assert_model_equal(expected: models.Chapter, result: Chapter) -> None:
    mapper = inspect(expected.__class__)
    for column in mapper.columns:
        if column.key == "id":
            continue
        assert getattr(expected, column.key) == getattr(result, column.key)


# ---- Tests ----------------------------------------------------------------------------


# ------------------
# create_chapter
# ------------------
@pytest.mark.asyncio
async def test_create_chapter_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup_books(testing_session)

    result = await services.create_chapter(
        ChapterCreate(book_id=1, number=1, title="test-chapter"),
        testing_session,
    )

    assert result.book_id == 1
    assert result.number == 1
    assert result.title == "test-chapter"


@pytest.mark.asyncio
async def test_create_chapter_raises_on_nonexistent_book(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(
        RelatedEntityDoesNotExistError, match="Book with id=1000 not found"
    ):
        await services.create_chapter(
            ChapterCreate(book_id=1000, number=1, title="test-chapter"),
            testing_session,
        )


# ------------------
# get_chapter
# ------------------
@pytest.mark.asyncio
async def test_get_chapter_happy_path(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await services.get_chapter(1, testing_session)

    assert_model_equal(data["x1"], result)


@pytest.mark.asyncio
async def test_get_chapter_raises_on_nonexistent_chapter(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Chapter with id=1000 not found"):
        await services.get_chapter(1000, testing_session)


# ------------------
# get_chapters
# ------------------
@pytest.mark.asyncio
async def test_get_chapters_happy_path(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await services.get_chapters(testing_session)

    assert len(result) == 4
    assert_model_equal(data["x1"], result[0])
    assert_model_equal(data["x2"], result[1])
    assert_model_equal(data["x3"], result[2])
    assert_model_equal(data["x4"], result[3])


@pytest.mark.asyncio
async def test_get_chapters_ordering(reset_db, testing_session: AsyncSession) -> None:
    await setup(testing_session)

    result = await services.get_chapters(testing_session)
    ids = [r.id for r in result]

    assert ids == sorted(ids)


@pytest.mark.asyncio
async def test_get_chapters_returns_empty_sequence(
    reset_db, testing_session: AsyncSession
) -> None:
    result = await services.get_chapters(testing_session)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_chapters_custom_page(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    result = await services.get_chapters(testing_session, page=1000)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_chapters_custom_size(
    reset_db, testing_session: AsyncSession
) -> None:
    data = await setup(testing_session)

    result = await services.get_chapters(testing_session, size=2)

    assert len(result) == 2
    assert_model_equal(data["x1"], result[0])
    assert_model_equal(data["x2"], result[1])


@pytest.mark.asyncio
async def test_get_chapters_custom_page_custom_size(
    reset_db, testing_session: AsyncSession
) -> None:
    data = await setup(testing_session)

    result = await services.get_chapters(testing_session, page=2, size=3)

    assert len(result) == 1
    assert_model_equal(data["x4"], result[0])


# ------------------
# update_chapter
# ------------------
@pytest.mark.asyncio
async def test_update_chapter_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    result = await services.update_chapter(
        1, ChapterUpdate(title="updated-chapter"), testing_session
    )

    assert result.book_id == 1
    assert result.number == 1
    assert result.title == "updated-chapter"


@pytest.mark.asyncio
async def test_update_chapter_raises_on_nonexistent_chapter(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Chapter with id=1000 not found"):
        await services.update_chapter(
            1000, ChapterUpdate(title="updated-chapter"), testing_session
        )


@pytest.mark.asyncio
async def test_update_chapter_raises_on_nonexistent_book(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(
        RelatedEntityDoesNotExistError, match="Book with id=1000 not found"
    ):
        await services.update_chapter(
            1, ChapterUpdate(book_id=1000, title="updated-chapter"), testing_session
        )


# ------------------
# delete_chapter
# ------------------
@pytest.mark.asyncio
async def test_delete_chapter_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    data = await setup(testing_session)

    result = await services.delete_chapter(1, testing_session)

    assert_model_equal(data["x1"], result)


@pytest.mark.asyncio
async def test_delete_chapter_raises_on_nonexistent_chapter(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Chapter with id=1000 not found"):
        await services.delete_chapter(1000, testing_session)
