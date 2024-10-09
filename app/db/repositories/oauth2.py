from enum import Enum
from sqlalchemy import insert, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OAuth2


class ClientHostname(str, Enum):
    HEADHUNTER = 'api.hh.ru'
    YANDEX = 'oauth.yandex.ru'


class OAuth2Repository:
    def __init__(self, session: AsyncSession) -> None:
        self.__session__ = session

    async def get(self, hostname: ClientHostname) -> OAuth2 | None:
        return await self.__session__.scalar(
            select(OAuth2).filter(hostname == OAuth2.hostname)
        )

    async def create(self, client: OAuth2) -> OAuth2:
        return await self.__session__.scalar(
            insert(OAuth2).values(
                access_token=client.access_token,
                refresh_token=client.refresh_token,
                expires_in=client.expires_in,
                hostname=client.hostname
            ).returning(OAuth2)
        )

    async def update(self, updated: OAuth2) -> OAuth2:
        return await self.__session__.scalar(
            update(OAuth2)
            .filter(updated.id == OAuth2.id)
            .values(
                access_token=updated.access_token,
                refresh_token=updated.refresh_token,
                expires_in=updated.expires_in,
                hostname=updated.hostname
            ).returning(OAuth2)
        )
