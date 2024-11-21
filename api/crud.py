from typing import TYPE_CHECKING, Iterable, cast

from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException
from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.dependencies import Container
from api.models import OfferORM, ProductORM
from api.schemas.offer import Offer
from api.schemas.product import ProductCreate, ProductUpdate

# TODO: implement more sofisticated Exception handling


@inject
async def create_product(
    product: ProductCreate,
    session=cast(AsyncSession, Provide[Container.session]),
) -> ProductORM:
    try:
        created_product = ProductORM(**product.model_dump())
        session.add(created_product)
        await session.commit()
        await session.refresh(created_product)
        return created_product
    except IntegrityError as e:
        logger.error(e)
        await session.rollback()
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
    return scalars.all()


@inject
async def read_products_with_offers(
    session=cast(AsyncSession, Provide[Container.session]),
) -> Iterable[ProductORM]:
    statement = select(ProductORM).options(selectinload(ProductORM.offers))
    scalars = await session.scalars(statement=statement)

    return scalars.all()


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
    await session.refresh(updated_product)
    return updated_product


@inject
async def delete_product(
    product: ProductORM, session=cast(AsyncSession, Provide[Container.session])
) -> ProductORM:
    try:
        await session.delete(product)
        await session.commit()
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
    await session.execute(statement)

    new_offers = [
        OfferORM(**offer.model_dump(), product_id=product_id)
        for offer in offers
        if offer.items_in_stock > 0
    ]
    session.add_all(new_offers)
    # ! running "await session.commit()" raises sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)
    # await session.commit()
    # !
    return new_offers
