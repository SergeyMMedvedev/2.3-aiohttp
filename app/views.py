import repository
from aiohttp.web import (
    HTTPUnauthorized,
    Request,
    Response,
    View,
    json_response,
)
from auth import check_password, hash_password
from errors import raise_http_error
from models import Advert, Token, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils import check_owner
from validators import (
    AdvertPatchValidator,
    AdvertValidator,
    UserPatchValidator,
    UserValidator,
    validate,
)


class Login(View):
    @validate(UserValidator)
    async def post(self) -> Response:
        """User login."""
        login_data = await self.request.json()
        query = select(User).where(User.email == login_data["email"])
        result = await self.request["session"].execute(query)
        user = result.scalar()
        if not user or not check_password(
            login_data["password"], user.password
        ):
            raise_http_error(HTTPUnauthorized, "incorrect login or password")

        token = Token(user=user)
        self.request["session"].add(token)
        await self.request["session"].commit()

        return json_response({"token": str(token.id)})


class UserView(View):
    def __init__(self, request: Request) -> None:
        super().__init__(request)
        self.repo = repository.SqlAlchemyRepository(self.session, User)

    @property
    def session(self) -> AsyncSession:
        """Get session."""
        return self.request['session']

    @property
    def user_id(self) -> int:
        """Get user_id."""
        return int(self.request.match_info['user_id'])

    async def get(self) -> Response:
        """Get User."""
        user = await self.repo.get(self.user_id)
        return json_response(
            {
                'msg': 'success',
                'data': {
                    'id': user.id,
                    'email': user.email,
                    'registration_time': user.registration_time.isoformat(),
                },
            }
        )

    @validate(UserValidator)
    async def post(self) -> Response:
        """Create user."""
        json_data = await self.request.json()
        json_data['password'] = hash_password(json_data['password'])
        user = User(**json_data)
        await self.repo.add(user)
        return json_response({'msg': 'done', 'data': {'id': user.id}})

    @validate(UserPatchValidator)
    async def patch(self) -> Response:
        """Update user data."""
        check_owner(self.request, self.user_id)
        user_data = await self.request.json()
        if "password" in user_data:
            user_data["password"] = hash_password(user_data["password"])
        await self.repo.update(user_data, self.user_id)
        return json_response({'msg': 'updated'})

    async def delete(self) -> Response:
        """Remove user."""
        check_owner(self.request, self.user_id)
        await self.repo.delete(self.user_id)
        return json_response({"status": "deleted"})


class AdvertView(View):
    def __init__(self, request: Request) -> None:
        super().__init__(request)
        self.repo = repository.SqlAlchemyRepository(self.session, Advert)

    @property
    def session(self) -> AsyncSession:
        """Get session."""
        return self.request['session']

    @property
    def advert_id(self) -> int:
        """Get advert_id."""
        return int(self.request.match_info['advert_id'])

    @property
    async def owner_id(self) -> int:
        """Get advert owner_id."""
        advert = await self.repo.get(self.advert_id)
        return int(advert.owner_id)  # type: ignore

    @property
    async def user_id(self) -> int:
        """Return token owner user_id."""
        return self.request["token"].user.id

    async def get(self) -> Response:
        """Get Advert."""
        advert = await self.repo.get(self.advert_id)
        return json_response(
            {
                'msg': 'success',
                'data': {
                    'id': advert.id,
                    'email': advert.title,
                    'description': advert.description,
                    'creation_time': advert.creation_time.isoformat(),
                    'owner': advert.owner.email,
                },
            }
        )

    @validate(AdvertValidator)
    async def post(self) -> Response:
        """Create advert."""
        json_data = await self.request.json()
        json_data['owner_id'] = await self.user_id
        advert = Advert(**json_data)
        await self.repo.add(advert)
        return json_response({'msg': 'done', 'data': {'id': advert.id}})

    @validate(AdvertPatchValidator)
    async def patch(self) -> Response:
        """Update advert data."""
        check_owner(self.request, await self.owner_id)
        advert_data = await self.request.json()
        await self.repo.update(advert_data, self.advert_id)
        return json_response({'msg': 'updated'})

    async def delete(self) -> Response:
        """Remove advert."""
        check_owner(self.request, await self.owner_id)
        await self.repo.delete(self.advert_id)
        return json_response({"status": "deleted"})
