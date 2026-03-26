from fastapi import Request
from fastapi.responses import JSONResponse

from src.exceptions import BookDigestApiError


async def book_digest_api_exception_handler(
    request: Request, exc: BookDigestApiError
) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})
