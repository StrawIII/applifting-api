from typing import AsyncGenerator

import httpx
from fastapi import HTTPException
from httpx import AsyncClient, Auth, HTTPStatusError, Request, RequestError, Response
from loguru import logger

from api.config import settings


class BearerAuth(Auth):
    def __init__(self, base_url: str, refresh_token: str) -> None:
        self.access_token = ""
        self.base_url = base_url
        self.refresh_token = refresh_token

    async def async_auth_flow(
        self,
        request: Request,
    ) -> AsyncGenerator[Request, Response]:
        """
        Interceps request/response flow and sets the Bearer access token.
        If the response is 401 UNAUTHORIZED it will fetch a new access token
        using the refresh token.
        """

        request.headers["Bearer"] = self.access_token
        logger.debug(self.access_token)
        response = yield request

        if response.status_code == httpx.codes.UNAUTHORIZED:
            # If the server issues a 401 UNAUTHORIZED response, then issue a request to
            # refresh the access token, and resend the request.
            self.access_token = await self.fetch_access_token()

            request.headers["Bearer"] = self.access_token
            yield request

        if response.status_code == httpx.codes.BAD_REQUEST:
            # tried to fetch a new access token while a valid access token still exists
            # possible fix: save last access token in the database or a file
            raise HTTPException(
                status_code=502,
                detail="Cannot obtain a new access token. Please try again later.",
            )

    async def fetch_access_token(self) -> str:
        try:
            # independant of the client object
            async with AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth",
                    headers={"Bearer": self.refresh_token},
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
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error response {e.response.status_code} while requesting {e.request.url!r}.",
            ) from e

        access_token = response.json().get("access_token")

        if access_token is None:
            raise HTTPException

        return access_token


client = AsyncClient(
    auth=BearerAuth(
        base_url=settings.applifting_api_base_url,
        refresh_token=settings.applifting_api_refresh_token,
    ),
    base_url=settings.applifting_api_base_url,
)
