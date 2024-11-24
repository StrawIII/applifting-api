import os
from uuid import UUID

from fastapi import APIRouter, Depends
from loguru import logger

from api.crud import (
    create_product,
    delete_product,
    read_offers,
    read_product,
    read_products,
    read_products_with_offers,
    update_product,
)
from api.dependencies import product_exists
from api.schemas.offer import Offer
from api.schemas.product import (
    ProductCatalogue,
    ProductCreateIn,
    ProductCreateOut,
    ProductDelete,
    ProductRead,
    ProductUpdateIn,
    ProductUpdateOut,
)
from api.utils import fetch_product_offers, register_product

router = APIRouter()


@router.get("/catalogue", summary="Get all products and their offers")
async def get_catalogue_() -> list[ProductCatalogue]:
    products = await read_products_with_offers()
    return [
        ProductCatalogue(
            id=product.id,
            name=product.name,
            description=product.description,
            offers=[Offer.model_validate(offer) for offer in product.offers],
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
        for product in products
    ]


@router.get("", summary="Get all products")
async def get_root_() -> list[ProductRead]:
    products = await read_products()
    return [ProductRead.model_validate(product) for product in products]


@router.post("", status_code=201, summary="Create a product")
async def post_root_(
    product: ProductCreateIn,
) -> ProductCreateOut:
    if os.getenv("ENVIRONMENT") == "testing":
        registered_product = product
    else:
        registered_product = await register_product(product=product)

    created_product = await create_product(product=registered_product)
    return ProductCreateOut.model_validate(created_product)


@router.get(
    "/{product_id}", dependencies=[Depends(product_exists)], summary="Get a product"
)
async def get_product_(product_id: UUID) -> ProductRead:
    product = await read_product(product_id=product_id)
    return ProductRead.model_validate(product)


# ? product_id query param coud be in body (kept as query param for consistent API)
@router.put(
    "/{product_id}", dependencies=[Depends(product_exists)], summary="Update a product"
)
async def put_product_(
    product_id: UUID,
    product: ProductUpdateIn,
):
    updated_product = await update_product(product_id=product_id, product=product)
    return ProductUpdateOut.model_validate(updated_product)


@router.delete(
    "/{product_id}", dependencies=[Depends(product_exists)], summary="Delete a product"
)
async def delete_product_(product_id: UUID) -> ProductDelete:
    product = await read_product(product_id=product_id)
    deleted_product = await delete_product(product=product)
    return ProductDelete.model_validate(deleted_product)


@router.get(
    "/{product_id}/offers",
    dependencies=[Depends(product_exists)],
    summary="Get product offers",
)
async def get_products_offers(product_id: UUID) -> list[Offer]:
    return await read_offers(product_id=product_id)
