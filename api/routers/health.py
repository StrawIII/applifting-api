import asyncio
from typing import cast

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import Container

router = APIRouter()


@router.get(
    "",
    status_code=204,
    summary="Check whether API is running and connetcted to the database.",
)
@inject
async def get_root(session=cast(AsyncSession, Provide[Container.session])) -> None:
    try:
        await asyncio.wait_for(session.execute(text("SELECT 1;")), timeout=5)
    except (asyncio.TimeoutError, OperationalError) as e:
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to the database.",
        ) from e

    return Response(status_code=204)
