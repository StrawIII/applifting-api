from __future__ import annotations

from asyncio import sleep
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID, uuid4

import httpx
from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import Settings
from api.crud import read_products, replace_offers
from api.database import engine
from api.dependencies import Container, _session
from api.schemas.offer import Offer

if TYPE_CHECKING:
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


@inject
async def fetch_product_offers(
    product_id: UUID, client=cast(AsyncClient, Provide[Container.client])
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
    settings=cast(Settings, Provide[Container.settings]),
    session=cast(AsyncSession, Provide[Container.session]),
) -> None:
    while True:
        logger.info("Retching offers...")
        products = await read_products()

        for product in products:
            print(product.name)
            offers = await fetch_product_offers(product_id=product.id)
            print(offers)
            await replace_offers(product_id=product.id, offers=offers, session=session)

        await sleep(settings.refetch_interval)
