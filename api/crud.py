from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import Sequence, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.models import OfferORM, ProductORM

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession

    from api.schemas.offer import Offer
    from api.schemas.product import ProductCreate

# TODO: implement more sofisticated Exception handling


async def create_product(
    product: ProductCreate,
    session: AsyncSession,
) -> ProductCreate:
    try:
        session.add(ProductORM(**product.model_dump()))
        await session.commit()

    except IntegrityError:
        pass
    except SQLAlchemyError as e:
        logger.error(e)
        await session.rollback()
        raise HTTPException from e

    return product


async def read_products(session: AsyncSession) -> Iterable[ProductORM]:
    statement = select(ProductORM)
    scalars = await session.scalars(statement=statement)
    return scalars.all()


async def read_product(product_id: UUID, session: AsyncSession) -> ProductORM:
    statement = select(ProductORM).where(ProductORM.id == product_id)
    scalars = await session.scalars(statement)
    product = scalars.one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


async def update_product(
    product_id: UUID,
    product: ProductORM,
    session: AsyncSession,
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


async def delete_product(product: ProductORM, session: AsyncSession) -> ProductORM:
    try:
        session.delete(product)
        session.commit()
    except SQLAlchemyError as e:
        logger.error(e)
        session.rollback()
        raise HTTPException(status_code=500, detail="Could not delete product") from e

    return product


async def read_offers(product_id: UUID, session: AsyncSession) -> Sequence[OfferORM]:
    statement = select(OfferORM).where(OfferORM.product_id == product_id)
    scalars = await session.scalars(statement)
    return scalars.all()


async def replace_offers(
    product_id: UUID,
    offers: list[Offer],
    session: AsyncSession,
) -> None:
    statement = select(OfferORM).where(OfferORM.product_id == product_id)
    scalars = await session.scalars(statement)
    existing_offers = scalars.all()

    try:
        for offer in existing_offers:
            await session.delete(offer)

        new_offers = [OfferORM(**offer.model_dump()) for offer in offers]
        session.add_all(new_offers)
        await session.commit()
    except SQLAlchemyError as e:
        logger.error(e)
        await session.rollback()
        raise HTTPException(status_code=500, detail="Could not replace offers") from e


# [
#   {
#     "id": "67ee0787-6b4e-2e87-44e6-c82d3fe8c053",
#     "price": 17782,
#     "items_in_stock": 336
#   },
#   {
#     "id": "52b6d267-693a-b550-2d4a-f1276699501e",
#     "price": 17295,
#     "items_in_stock": 325
#   },
#   {
#     "id": "72c3b061-989b-324b-ad19-2735a00c288d",
#     "price": 17765,
#     "items_in_stock": 32
#   }
# ]
