from sqlalchemy.ext.asyncio import create_async_engine

from api.config import settings

engine = create_async_engine(settings.postgres_url, echo=True)
