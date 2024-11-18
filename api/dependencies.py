from typing import Annotated, Any, AsyncGenerator
from uuid import UUID

from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import Settings
from api.models import ProductORM
from api.schemas.product import ProductCreate


async def _settings() -> Settings:
    from api.config import settings

    return settings


async def _session() -> AsyncGenerator[AsyncSession, Any]:
    from api.database import engine

    async with AsyncSession(engine) as session:
        yield session


async def _client() -> AsyncClient:
    from api.client import client

    return client


async def _product_by_name(product_id: UUID, session: "SessionDep") -> ProductORM:
    from api.crud import read_product

    return await read_product(product_if=product_id, session=session)


SettingsDep = Annotated[Settings, Depends(_settings)]
SessionDep = Annotated[AsyncSession, Depends(_session)]
ClientDep = Annotated[AsyncClient, Depends(_client)]
ProductDep = Annotated[ProductORM, Depends(_product_by_name)]
RegisteredProductDep = Annotated[ProductCreate, Depends(...)]


class Container(DeclarativeContainer):
    settings = providers.Singleton(_settings)
    session = providers.Resource(_session)
    client = providers.Singleton(_client)
