class BookDigestApiError(Exception):
    """Base exception class for the Book Digest API."""

    status_code: int = 500
    code: str = "book_digest_api_error"

    def __init__(self, message: str | None = None):
        self.message = message or "Service is unavailable"
        super().__init__(self.message)


class EntityDoesNotExistError(BookDigestApiError):
    """Entity not found."""

    status_code = 404
    code = "entity_not_found"


class EntityAlreadyExistsError(BookDigestApiError):
    """Entity already exists."""

    status_code = 409
    code = "entity_already_exists"


class RelatedEntityDoesNotExistError(BookDigestApiError):
    """Related entity not found."""

    status_code = 422
    code = "related_entity_not_found"


class ServiceError(BookDigestApiError):
    """External service or DB failure."""

    status_code = 503
    code = "service_error"
