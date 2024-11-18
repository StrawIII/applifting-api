from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from api.client import client
from api.config import settings
from api.database import engine
from api.models import Base
from api.routers import health, products
from api.utils import fetch_loop


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[FastAPI, None]:
    async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        await fetch_loop(5.0, session=session, client=client)

    yield

    await client.aclose()


# ? root_path could be set in NGINX instead using .env
app = FastAPI(
    title=settings.project_name,
    lifespan=lifespan,
    root_path=settings.api_prefix,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(products.router, prefix="/products", tags=["products"])
