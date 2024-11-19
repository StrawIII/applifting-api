from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from loguru import logger

from api.crud import (
    create_product,
    delete_product,
    read_product,
    read_products,
    update_product,
)
from api.schemas.offer import Offer
from api.schemas.product import (
    ProductCreate,
    ProductDelete,
    ProductRead,
    ProductUpdate,
)
from api.utils import fetch_product_offers, register_product

router = APIRouter()


# TODO: add offers
@router.get("", summary="Get all products and their offers")
async def get_root_() -> list[ProductRead]:
    products = await read_products()
    return [ProductRead.model_validate(product) for product in products]


@router.post("", status_code=201, summary="Create a product")
async def post_root_(
    product: ProductCreate,
) -> ProductCreate:
    registered_product = await register_product(product=product)
    created_product = await create_product(product=registered_product)
    logger.info(created_product.name)
    return ProductCreate.model_validate(created_product)


@router.get("/{product_id}", summary="Get a product")
async def get_product_(product_id: UUID) -> ProductRead:
    product = await read_product(product_id=product_id)
    return ProductRead.model_validate(product)


# ? product_id query param coud be in body (kept as query param for consistent API)
@router.put("/{product_id}", summary="Update a product")
async def put_product_(
    product_id: UUID,
    product: ProductUpdate,
):
    updated_product = await update_product(product_id=product_id, product=product)
    return ProductUpdate.model_validate(updated_product)


@router.delete("/{product_id}", summary="Delete a product")
async def delete_product_(product_id: UUID) -> ProductDelete:
    product = await read_product(product_id=product_id)
    deleted_product = await delete_product(product=product)
    return ProductDelete.model_validate(deleted_product)


@router.get("/{product_id}/offers", summary="Get product offers")
async def get_products_offers(product_id: UUID) -> list[Offer]:
    return [
        Offer.model_validate(offer)
        for offer in await fetch_product_offers(product_id=product_id)
    ]
