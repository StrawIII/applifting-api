from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, cast

from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException
from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import Container
from api.models import OfferORM, ProductORM

if TYPE_CHECKING:
    from uuid import UUID

    from api.schemas.offer import Offer
    from api.schemas.product import ProductCreate

# TODO: implement more sofisticated Exception handling


async def create_product(
    product: ProductCreate,
) -> ProductCreate:
    session=cast(AsyncSession, Provide[Container.session]),
    try:
        session.add(ProductORM(**product.model_dump()))
        await session.commit()

    except IntegrityError:
        pass
    except SQLAlchemyError as e:
        logger.error(e)
        await session.rollback()
        raise HTTPException from e


@inject
async def read_products(
    session=cast(AsyncSession, Provide[Container.session]),
) -> Iterable[ProductORM]:
    statement = select(ProductORM)
    scalars = await session.scalars(statement=statement)
    return scalars.unique()


@inject
async def read_product(
    product_id: UUID, session=cast(AsyncSession, Provide[Container.session])
) -> ProductORM:
    statement = select(ProductORM).where(ProductORM.id == product_id)
    scalars = await session.scalars(statement)
    product = scalars.one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@inject
async def update_product(
    product_id: UUID,
    product: ProductUpdate,
    session=cast(AsyncSession, Provide[Container.session]),
) -> ProductORM:
    updated_product = await session.merge(
        ProductORM(
            id=product_id,
            name=product.name,
            description=product.description,
        ),
    )
    await session.commit()
    return updated_product


@inject
async def delete_product(
    product: ProductORM, session=cast(AsyncSession, Provide[Container.session])
) -> ProductORM:
    try:
        session.delete(product)
        session.commit()
    except SQLAlchemyError as e:
        logger.error(e)
        session.rollback()
        raise HTTPException(status_code=500, detail="Could not delete product") from e

    return product


@inject
async def read_offers(
    product_id: UUID, session=cast(AsyncSession, Provide[Container.session])
) -> Iterable[OfferORM]:
    statement = select(OfferORM).where(OfferORM.product_id == product_id)
    scalars = await session.scalars(statement)
    return scalars.all()


@inject
async def replace_offers(
    product_id: UUID,
    offers: list[Offer],
    session=cast(AsyncSession, Provide[Container.session]),
) -> Iterable[OfferORM]:
    statement = delete(OfferORM).where(OfferORM.product_id == product_id)
    scalars = await session.scalars(statement)
    # existing_offers = scalars.all()

    # for offer in existing_offers:
    #     await session.delete(offer)

    new_offers = [
        OfferORM(**offer.model_dump(), product_id=product_id) for offer in offers
    ]
