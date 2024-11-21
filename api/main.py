import asyncio
import os
import subprocess
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import crud, utils
from api.client import client
from api.config import settings
from api.dependencies import Container
from api.routers import health, products
from api.utils import fetch_loop

container = Container()
container.wire(modules=[utils, crud, health])


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[FastAPI, None]:
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    if os.getenv("ENVIRONMENT") != "testing":
        asyncio.create_task(fetch_loop(), name="fetch_loop")

    try:
        yield
    finally:
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


# @app.middleware("http")
# async def logging_middleware(
#     request: Request, call_next: Coroutine[None, Request, Response]
# ):
#     request_body = await request.body()
#     response = await call_next(request)
