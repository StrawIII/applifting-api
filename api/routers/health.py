import asyncio

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from api.dependencies import SessionDep

router = APIRouter()


@router.get(
    "",
    status_code=204,
    summary="Check whether API is running and connetcted to the database.",
)
async def get_root(session: SessionDep) -> None:
    try:
        await asyncio.wait_for(session.execute(text("SELECT 1;")), timeout=1)
    except (asyncio.TimeoutError, OperationalError) as e:
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to the database.",
        ) from e

    return Response(status_code=204)
