from typing import cast, Sequence
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Contact


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.__session__ = session

    async def get_all(self) -> Sequence[Contact]:
        result = await self.__session__.scalars(select(Contact))

        return result.fetchall()

    async def create(self, contact: Contact) -> Contact:
        self.__session__.add(contact)
        await self.__session__.refresh(contact)

        return contact

    async def get(self, contact_id: int) -> Contact | None:
        return await self.__session__.get(Contact, contact_id)

    async def update(self, updated: Contact) -> Contact:
        return await self.__session__.scalar(
            update(Contact)
            .filter(updated.id == Contact.id)
            .values(**updated.__dict__)
            .returning(Contact)
        )

    async def delete(self, contact_id: int) -> None:
        raise RuntimeError("Deleting contacts is prohibited")
