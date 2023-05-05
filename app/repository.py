from aiohttp.web import HTTPForbidden, HTTPNotFound
from errors import raise_http_error
from models import ORM_TYPE
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyRepository:
    def __init__(self, session: AsyncSession, model: ORM_TYPE) -> None:
        self.model = model
        self.session = session

    async def add(self, orm_item: ORM_TYPE) -> None:
        """Add orm item."""
        self.session.add(orm_item)
        try:
            await self.session.commit()
        except IntegrityError:
            raise raise_http_error(
                HTTPForbidden, f"{self.model.__name__} already exists!"
            )

    async def get(self, model_id) -> ORM_TYPE:
        """Get model instance by id."""
        item = await self.session.get(self.model, model_id)
        if item is None:
            raise raise_http_error(
                HTTPNotFound, f"{self.model.__name__} not found"
            )
        return item

    async def update(self, data_json, model_id) -> None:
        """Update orm item."""
        item = await self.get(model_id)
        for field, value in data_json.items():
            setattr(item, field, value)
        await self.add(item)

    async def delete(self, model_id) -> None:
        """Delete orm_item."""
        item = await self.get(model_id)
        await self.session.delete(item)
        await self.session.commit()
