import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.crud import digests
from src.exceptions import EntityDoesNotExistError
from src.schemas import DigestCreate, DigestUpdate

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


async def setup_chapters(session: AsyncSession) -> None:
    await setup_books(session)

    c1 = models.Chapter(id=1, book_id=1, number=1, title="test-chapter")
    c2 = models.Chapter(id=2, book_id=2, number=2)
    c3 = models.Chapter(id=3, book_id=3, number=3, title="other-chapter")
    c4 = models.Chapter(id=4, book_id=4, number=4)

    session.add_all([c1, c2, c3, c4])
    await session.commit()


async def setup(session: AsyncSession) -> dict[str, models.Digest]:
    await setup_chapters(session)

    x1 = models.Digest(id=1, chapter_id=1, paragraph_number=1, digest="test-digest")
    x2 = models.Digest(id=2, chapter_id=1, paragraph_number=1, digest="test-digest")
    x3 = models.Digest(id=3, chapter_id=1, paragraph_number=1, digest="test-digest")
    x4 = models.Digest(id=4, chapter_id=1, paragraph_number=1, digest="test-digest")

    all_digests = {"x1": x1, "x2": x2, "x3": x3, "x4": x4}

    session.add_all(all_digests.values())
    await session.commit()

    return all_digests


def assert_model_equal(expected: models.Digest, result: models.Digest) -> None:
    mapper = inspect(expected.__class__)
    for column in mapper.columns:
        if column.key == "id":
            continue
        assert getattr(expected, column.key) == getattr(result, column.key)


# ---- Tests ----------------------------------------------------------------------------


# -----------------
# create_digest
# -----------------
@pytest.mark.asyncio
async def test_create_digest_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup_chapters(testing_session)

    result = await digests.create_digest(
        DigestCreate(chapter_id=1, paragraph_number=1, digest="test-digest"),
        testing_session,
    )

    assert result.chapter_id == 1
    assert result.paragraph_number == 1
    assert result.digest == "test-digest"


# -----------------
# find_digest
# -----------------
@pytest.mark.asyncio
async def test_find_digest_happy_path(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await digests.find_digest(1, testing_session)

    assert_model_equal(data["x1"], result)


@pytest.mark.asyncio
async def test_find_digest_raises_on_nonexistent_digest(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Digest with id=1000 not found"):
        await digests.find_digest(1000, testing_session)


# -----------------
# find_digests
# -----------------
@pytest.mark.asyncio
async def test_find_digests_happy_path(reset_db, testing_session: AsyncSession) -> None:
    data = await setup(testing_session)

    result = await digests.find_digests(testing_session)

    assert len(result) == 4
    assert_model_equal(data["x1"], result[0])
    assert_model_equal(data["x2"], result[1])
    assert_model_equal(data["x3"], result[2])
    assert_model_equal(data["x4"], result[3])


@pytest.mark.asyncio
async def test_find_digests_ordering(reset_db, testing_session: AsyncSession) -> None:
    await setup(testing_session)

    result = await digests.find_digests(testing_session)
    ids = [r.id for r in result]

    assert ids == sorted(ids)


@pytest.mark.asyncio
async def test_find_digests_returns_empty_sequence(
    reset_db, testing_session: AsyncSession
) -> None:
    result = await digests.find_digests(testing_session)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_find_digests_custom_page(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    result = await digests.find_digests(testing_session, page=1000)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_find_digests_custom_size(
    reset_db, testing_session: AsyncSession
) -> None:
    data = await setup(testing_session)

    result = await digests.find_digests(testing_session, size=2)

    assert len(result) == 2
    assert_model_equal(data["x1"], result[0])
    assert_model_equal(data["x2"], result[1])


@pytest.mark.asyncio
async def test_find_digests_custom_page_custom_size(
    reset_db, testing_session: AsyncSession
) -> None:
    data = await setup(testing_session)

    result = await digests.find_digests(testing_session, page=2, size=3)

    assert len(result) == 1
    assert_model_equal(data["x4"], result[0])


# -----------------
# update_digest
# -----------------
@pytest.mark.asyncio
async def test_update_digest_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    result = await digests.update_digest(
        1, DigestUpdate(digest="updated-digest"), testing_session
    )

    assert result.chapter_id == 1
    assert result.paragraph_number == 1
    assert result.digest == "updated-digest"


@pytest.mark.asyncio
async def test_update_digest_raises_on_nonexistent_digest(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Digest with id=1000 not found"):
        await digests.update_digest(
            1000, DigestUpdate(digest="updated-digest"), testing_session
        )


# -----------------
# delete_digest
# -----------------
@pytest.mark.asyncio
async def test_delete_digest_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    data = await setup(testing_session)

    result = await digests.delete_digest(1, testing_session)

    assert_model_equal(data["x1"], result)


@pytest.mark.asyncio
async def test_delete_digest_raises_on_nonexistent_digest(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    with pytest.raises(EntityDoesNotExistError, match="Digest with id=1000 not found"):
        await digests.delete_digest(1000, testing_session)


# -----------------
# count_all_digests
# -----------------
@pytest.mark.asyncio
async def test_count_all_digests_happy_path(
    reset_db, testing_session: AsyncSession
) -> None:
    await setup(testing_session)

    result = await digests.count_all_digests(testing_session)

    assert result == 4


@pytest.mark.asyncio
async def test_count_all_digests_returns_zeroes(
    reset_db, testing_session: AsyncSession
) -> None:
    result = await digests.count_all_digests(testing_session)

    assert result == 0
