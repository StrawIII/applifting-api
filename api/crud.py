from __future__ import annotations

from typing import Iterable, cast
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException
from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.exc import (
    DatabaseError,
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.exc import StaleDataError

from api.dependencies import Container
from api.models import OfferORM, ProductORM
from api.schemas.offer import Offer
from api.schemas.product import ProductCreateIn, ProductUpdateIn

# TODO: implement more sofisticated Exception handling


@inject
async def create_product(
    product: ProductCreateIn,
    session=cast(AsyncSession, Provide[Container.session]),
) -> ProductORM:
    try:
        created_product = ProductORM(**product.model_dump())
        session.add(created_product)
        await session.commit()
        await session.refresh(created_product)
        return created_product
    except IntegrityError as e:
        logger.error(f"Integrity error while creating product: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="Product with this ID already exists"
        ) from e
    except DatabaseError as e:
        logger.error(f"Database error while creating product: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Database error occurred while creating the product"
        ) from e
    except SQLAlchemyError as e:
        logger.error(f"Unexpected SQLAlchemy error while creating product: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while creating the product",
        ) from e


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
    try:
        statement = select(ProductORM).where(ProductORM.id == product_id)
        scalars = await session.scalars(statement)
        product = scalars.one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Database error while reading product {product_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Error occurred while fetching the product"
        ) from e
    else:
        return product


@inject
async def update_product(
    product_id: UUID,
    product: ProductUpdateIn,
    session=cast(AsyncSession, Provide[Container.session]),
) -> ProductORM:
    try:
        updated_product = await session.merge(
            ProductORM(
                id=product_id,
                name=product.name,
                description=product.description,
            ),
        )
        await session.commit()
        await session.refresh(updated_product)
    except StaleDataError as e:
        logger.error(f"Concurrent update detected for product {product_id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Product was modified by another request. Please try again",
        ) from e
    except IntegrityError as e:
        logger.error(f"Integrity error while updating product {product_id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="Update violates database constraints"
        ) from e
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating product {product_id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Error occurred while updating the product"
        ) from e
    else:
        return updated_product


@inject
async def delete_product(
    product: ProductORM, session=cast(AsyncSession, Provide[Container.session])
) -> ProductORM:
    try:
        await session.delete(product)
        await session.commit()
    except IntegrityError as e:
        logger.error(f"Integrity error while deleting product {product.id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="Cannot delete product due to existing references"
        ) from e
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting product {product.id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Error occurred while deleting the product"
        ) from e
    else:
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
    try:
        statement = delete(OfferORM).where(OfferORM.product_id == product_id)
        await session.execute(statement)

        new_offers = [
            OfferORM(
                **offer.model_dump(exclude={"id"}),
                id=offer.id if isinstance(offer.id, UUID) else UUID(offer.id),
                product_id=product_id,
            )
            for offer in offers
            if offer.items_in_stock > 0
        ]
        session.add_all(new_offers)
        await session.commit()
    except IntegrityError as e:
        logger.error(
            f"Integrity error while replacing offers for product {product_id}: {e}"
        )
        await session.rollback()
    except SQLAlchemyError as e:
        logger.error(
            f"Database error while replacing offers for product {product_id}: {e}"
        )
        await session.rollback()
    else:
        return new_offers
