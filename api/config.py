from typing import NewType

import sqlalchemy
from dotenv import find_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

Seconds = NewType("Seconds", float)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")

    environment: str

    project_name: str = "applifting-api"
    api_prefix: str = "/api/v1"
    refetch_interval: Seconds = Seconds(60.0)

    cors_allowed_origins: list[str] = ["*"]
    cors_allowed_credentials: bool = True
    cors_allowed_methods: list[str] = ["*"]
    cors_allowed_headers: list[str] = ["*"]

    applifting_api_base_url: str
    applifting_api_refresh_token: str

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_database: str

    @computed_field
    @property
    def postgres_url(self) -> sqlalchemy.URL:
        return sqlalchemy.URL.create(
            drivername="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_database,
        )


settings = Settings()
