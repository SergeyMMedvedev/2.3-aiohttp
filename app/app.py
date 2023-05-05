from typing import AsyncGenerator

from aiohttp.web import Application, delete, get, patch, post, run_app
from middlewares import auth_middleware, session_middleware
from models import Base, engine
from views import AdvertView, Login, UserView


async def app_context(app: Application) -> AsyncGenerator:
    """Context for application."""
    print('START')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print('SHUT DOWN')


async def get_app() -> Application:
    """Return aiohttp application."""
    app = Application()
    app.middlewares.append(session_middleware)
    app_auth_required = Application(
        middlewares=[session_middleware, auth_middleware]
    )
    app_adv_auth_required = Application(
        middlewares=[session_middleware, auth_middleware]
    )

    app.cleanup_ctx.append(app_context)
    app.add_routes(
        [
            post("/login", Login),
            post("/users", UserView),
            get("/adverts/{advert_id:\d+}", AdvertView),
        ]
    )

    app_auth_required.add_routes(
        [
            get("/{user_id:\d+}", UserView),
            patch("/{user_id:\d+}", UserView),
            delete("/{user_id:\d+}", UserView),
        ]
    )
    app_adv_auth_required.add_routes(
        [
            post("", AdvertView),
            patch("/{advert_id:\d+}", AdvertView),
            delete("/{advert_id:\d+}", AdvertView),
        ]
    )
    app.add_subapp(prefix="/users", subapp=app_auth_required)
    app.add_subapp(prefix="/adverts", subapp=app_adv_auth_required)
    return app


run_app(get_app())
