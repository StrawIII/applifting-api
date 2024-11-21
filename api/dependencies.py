from typing import Annotated, Any, AsyncGenerator
from uuid import UUID

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Resource, Singleton
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.client import client
from api.config import settings
from api.models import ProductORM


async def _session() -> AsyncGenerator[AsyncSession, Any]:
    from api.database import engine

    async with AsyncSession(engine) as session:
        yield session


async def product_exists(product_id: UUID, session: "SessionDep") -> None:
    statement = select(ProductORM).where(ProductORM.id == product_id)
    scalars = await session.scalars(statement)
    product = scalars.one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")


SessionDep = Annotated[AsyncSession, Depends(_session)]


class Container(DeclarativeContainer):
    settings = Singleton(lambda: settings)
    session = Resource(_session)
    client = Singleton(lambda: client)
