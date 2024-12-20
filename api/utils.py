from asyncio import sleep
from typing import Any, cast
from uuid import UUID, uuid4

import httpx
from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import Settings
from api.crud import read_products, replace_offers
from api.dependencies import Container
from api.schemas.offer import Offer
from api.schemas.product import ProductCreateIn


@inject
async def register_product(
    product: ProductCreateIn,
    client: AsyncClient = Provide[Container.client],
) -> ProductCreateIn:
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
            product = await register_product(product=product)

    return product


@inject
async def fetch_product_offers(
    product_id: UUID, client: AsyncClient = Provide[Container.client]
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


@inject
async def fetch_loop(
    settings: Settings = Provide[Container.settings],
    session: AsyncSession = Provide[Container.session],
) -> None:
    while True:
        products = await read_products()

        for product in products:
            logger.info(f"fetching offers for product {product.name}")
            offers = await fetch_product_offers(product_id=product.id)
            await replace_offers(product_id=product.id, offers=offers)

        await session.commit()
        await sleep(settings.refetch_interval)
