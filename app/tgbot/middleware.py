from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Awaitable, Dict, Any


class DatabaseSessionMiddleware(BaseMiddleware):
    def __init__(self, session: AsyncSession) -> None:
        self.__session__ = session

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data['session'] = self.__session__

        return await handler(event, data)
