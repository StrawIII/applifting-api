from typing import Annotated, Any, AsyncGenerator
from uuid import UUID

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Resource, Singleton
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.client import client
from api.config import settings
from api.models import ProductORM


async def _session() -> AsyncGenerator[AsyncSession, Any]:
    from api.database import engine

    async with AsyncSession(engine) as session:
        yield session


async def _product_by_name(product_id: UUID, session: "SessionDep") -> ProductORM:
    from api.crud import read_product

    return await read_product(product_if=product_id, session=session)


SessionDep = Annotated[AsyncSession, Depends(_session)]
ProductDep = Annotated[ProductORM, Depends(_product_by_name)]


class Container(DeclarativeContainer):
    settings = Singleton(lambda: settings)
    session = Resource(_session)
    client = Singleton(lambda: client)
