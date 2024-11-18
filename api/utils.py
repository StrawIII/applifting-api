from __future__ import annotations

from asyncio import sleep
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID, uuid4

import httpx
from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError
from loguru import logger

from api.crud import read_products, replace_offers
from api.schemas.offer import Offer

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from api.schemas.product import ProductCreate


async def register_product(
    product: ProductCreate,
    client: AsyncClient,
) -> ProductCreate:
    try:
        response = await client.post(
            "/products/register",
            json=product.model_dump(),
        )
        response.raise_for_status()
    except RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}.")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Please try again later.",
        ) from e
    except HTTPStatusError as e:
        logger.error(
            f"Error response {e.response.status_code} while requesting {e.request.url!r}.",
        )
        if e.response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Could not register product.",
            ) from e

        if e.response.status_code == httpx.codes.CONFLICT:
            product.id = uuid4()
            product = await register_product(product=product, client=client)

    return product


async def fetch_product_offers(
    product_id: UUID,
    client: AsyncClient,
) -> list[Offer]:
    try:
        response = await client.get(f"/products/{product_id}/offers")
        response.raise_for_status()
    except RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}.")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Please try again later.",
        ) from e
    except HTTPStatusError as e:
        logger.error(
            f"Error response {e.response.status_code} while requesting {e.request.url!r}.",
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Status error",
        ) from e

    return [Offer(**offer) for offer in cast(list[dict[str, Any]], response.json())]


async def fetch_loop(
    interval: float,
    session: AsyncSession,
    client: AsyncClient,
) -> None:
    logger.info("fetching...")
    products = await read_products(session=session)

    while True:
        for product in products:
            offers = await fetch_product_offers(product_id=product.id, client=client)
            await replace_offers(product_id=product.id, offers=offers, session=session)

        await sleep(interval)
