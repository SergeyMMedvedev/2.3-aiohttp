from aiohttp.web import HTTPForbidden, Request
from errors import raise_http_error


def check_owner(request: Request, user_id: int | None) -> None:
    """Check user is owner."""
    if not request["token"] or request["token"].user.id != user_id:
        raise_http_error(HTTPForbidden, "only owner has access")
