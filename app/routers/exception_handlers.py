from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from app.exceptions import NotFoundException, InvalidPageException, ForbiddenException


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, NotFoundException)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def invalid_page_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, InvalidPageException)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def forbidden_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ForbiddenException)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
    )
