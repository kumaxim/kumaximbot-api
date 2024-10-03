from typing import cast, List, Sequence
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Post


class PostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.__session__ = session

    async def get_all(self) -> Sequence[Post]:
        result = await self.__session__.scalars(select(Post))
        return result.fetchall()

    async def create(self, post: Post) -> Post:
        async with self.__session__.begin():
            self.__session__.add(post)

        await self.__session__.refresh(post)

        return post

    async def get(self, post_id: int) -> Post | None:
        return await self.__session__.get(Post, post_id)

    async def get_by_command_name(self, name: str) -> Post | None:
        return await self.__session__.scalar(select(Post).filter_by(command=name))

    async def update(self, updated: Post):
        async with self.__session__.begin():
            return await self.__session__.scalar(
                update(Post)
                .where(cast('ColumnElement[bool]', Post.id == updated.id))
                .values(text=updated.text, command=updated.command)
                .returning(Post)
            )

    async def delete(self, post_id: int) -> None:
        async with self.__session__.begin():
            await self.__session__.execute(delete(Post).where(cast('ColumnElement[bool]', Post.id == post_id)))
