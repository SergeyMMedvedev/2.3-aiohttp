import json
from typing import Type

from aiohttp.web import HTTPForbidden, HTTPNotFound, HTTPUnauthorized

ERROR_TYPE = Type[HTTPUnauthorized] | Type[HTTPForbidden] | Type[HTTPNotFound]


def raise_http_error(
    error_class: ERROR_TYPE, message: str | dict
) -> ERROR_TYPE:
    """Raise http error."""
    raise error_class(
        text=json.dumps({"status": "error", "description": message}),
        content_type="application/json",
    )
