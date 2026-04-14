from fastapi import Request
from fastapi.responses import JSONResponse

from src.exceptions import BookDigestApiError


async def book_digest_api_exception_handler(
    request: Request, exc: BookDigestApiError
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, content={"code": exc.code, "message": exc.message}
    )
