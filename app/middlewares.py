import datetime
from typing import Awaitable, Callable

from aiohttp.web import (
    HTTPForbidden,
    HTTPNotFound,
    Request,
    StreamResponse,
    middleware,
)
from config import TOKEN_TTL
from errors import raise_http_error
from models import Session, Token
from repository import SqlAlchemyRepository


@middleware
async def session_middleware(
    request: Request, handler: Callable[[Request], Awaitable[StreamResponse]]
) -> StreamResponse:
    """Middleware for sqlalchemy session."""
    async with Session() as session:
        request["session"] = session
        return await handler(request)


@middleware
async def auth_middleware(
    request: Request, handler: Callable[[Request], Awaitable[StreamResponse]]
) -> StreamResponse:
    """Middleware for user authentication."""
    token_id = request.headers.get("token")
    if not token_id:
        raise_http_error(HTTPForbidden, "incorrect token")
    try:
        repo = SqlAlchemyRepository(request["session"], Token)
        token = await repo.get(token_id)
    except HTTPNotFound:
        token = None
    if (
        not token
        or (token.creation_time
            + datetime.timedelta(seconds=TOKEN_TTL))  # type: ignore
        <= datetime.datetime.now()
    ):
        raise_http_error(HTTPForbidden, "incorrect token")
    request["token"] = token
    return await handler(request)
