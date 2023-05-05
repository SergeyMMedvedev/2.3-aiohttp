import json
from typing import Callable, Optional

from aiohttp.web import Response, json_response
from pydantic import BaseModel, Extra
from pydantic.error_wrappers import ValidationError


class UserValidator(BaseModel, extra=Extra.forbid):
    email: str
    password: str


class UserPatchValidator(BaseModel, extra=Extra.forbid):
    email: Optional[str]
    password: Optional[str]


class AdvertValidator(BaseModel, extra=Extra.forbid):
    title: str
    description: str


class AdvertPatchValidator(BaseModel, extra=Extra.forbid):
    title: Optional[str]
    description: Optional[str]


def validate(base_model) -> Callable:
    """Validate decorator."""
    def decorator(handler) -> Callable:
        async def wrapper(view) -> Response:
            json_data = await view.request.json()
            try:
                base_model(**json_data)
            except ValidationError as e:
                return json_response(
                    {'error': json.loads(e.json())}, status=400
                )
            return await handler(view)
        return wrapper
    return decorator
