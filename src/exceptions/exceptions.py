from fastapi import status


class BookDigestApiError(Exception):
    """Base exception class for the Book Digest API."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "book_digest_api_error"

    def __init__(self, message: str | None = None):
        self.message = message or "Service is unavailable"
        super().__init__(self.message)


class EntityDoesNotExistError(BookDigestApiError):
    """Entity not found."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "entity_not_found"


class EntityAlreadyExistsError(BookDigestApiError):
    """Entity already exists."""

    status_code = status.HTTP_409_CONFLICT
    code = "entity_already_exists"


class RelatedEntityDoesNotExistError(BookDigestApiError):
    """Related entity not found."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "related_entity_not_found"


class ServiceError(BookDigestApiError):
    """External service or DB failure."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "service_error"
