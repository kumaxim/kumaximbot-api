from types import NoneType
from typing import cast, Sequence
from sqlalchemy import insert, delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Post


class PostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.__session__ = session

    async def get_all(self) -> Sequence[Post]:
        result = await self.__session__.scalars(select(Post))

        return result.fetchall()

    async def create(self, post: Post) -> Post:
        return await self.__session__.scalar(
            insert(Post)
            .values(
                title=post.title,
                text=post.text,
                command=post.command,
                callback_query=post.callback_query
            ).returning(Post)
        )

    async def get(self, post_id: int) -> Post | None:
        return await self.__session__.get(Post, post_id)

    async def get_by_command_name(
            self,
            name: str,
            include_callback_queries: bool = False
    ) -> Sequence[Post] | Post | NoneType:
        if not include_callback_queries:
            return await self.__session__.scalar(
                select(Post).filter_by(command=name).filter(Post.callback_query.is_(None))
            )

        result = await self.__session__.scalars(select(Post).filter_by(command=name))

        return result.fetchall()

    async def filter_by(self, **kwargs: str | int | None) -> Sequence[Post] | None:
        query = select(Post)

        for key, value in kwargs.items():
            if hasattr(Post, key):
                query = query.filter(getattr(Post, key) == value)

        result = await self.__session__.scalars(query.order_by(Post.command))

        return result.fetchall()

    async def update(self, updated: Post) -> Post:
        return await self.__session__.scalar(
            update(Post)
            .filter(updated.id == Post.id)
            .values(
                title=updated.title,
                text=updated.text,
                command=updated.command,
                callback_query=updated.callback_query
            ).returning(Post)
        )

    async def delete(self, post_id: int) -> None:
        await self.__session__.execute(delete(Post).where(cast('ColumnElement[bool]', Post.id == post_id)))
