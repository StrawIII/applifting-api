from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from api.crud import create_product, delete_product, read_product, read_products
from api.dependencies import ClientDep, SessionDep
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
async def get_root_(session: SessionDep) -> list[ProductRead]:
    products = await read_products(session=session)
    return [ProductRead.model_validate(product) for product in products]


@router.post("", status_code=201, summary="Create a product")
async def post_root_(
    product: ProductCreate,
    session: SessionDep,
    httpx_client: ClientDep,
) -> ProductCreate:
    registered_product = await register_product(
        product=product,
        client=httpx_client,
    )
    created_product = await create_product(product=registered_product, session=session)
    return ProductCreate.model_validate(created_product)


@router.get("/{product_id}", summary="Get a product")
async def get_product_(product_id: UUID, session: SessionDep) -> ProductRead:
    product = await read_product(product_id=product_id, session=session)
    return ProductRead.model_validate(product)


# TODO: finish
@router.put("/{product_id}", summary="Update a product")
async def put_product_(
    product_id: UUID,
    product_: ProductUpdate,
    session: SessionDep,
):
    product = await read_product(product_id=product_id, session=session)


@router.delete("/{product_id}", summary="Delete a product")
async def delete_product_(product_id: UUID, session: SessionDep) -> ProductDelete:
    product = await read_product(product_id=product_id, session=session)
    deleted_product = await delete_product(product=product, session=session)
    return ProductDelete.model_validate(deleted_product)


@router.get("/{product_id}/offers", summary="Get product offers")
async def get_products_offers(product_id: UUID, client: ClientDep) -> list[Offer]:
    return [
        Offer.model_validate(offer)
        for offer in await fetch_product_offers(product_id=product_id, client=client)
    ]
