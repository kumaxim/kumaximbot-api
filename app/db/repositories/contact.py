from typing import Sequence
from sqlalchemy import insert, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Contact


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.__session__ = session

    async def get_all(self) -> Sequence[Contact]:
        result = await self.__session__.scalars(select(Contact))

        return result.fetchall()

    async def create(self, contact: Contact) -> Contact:
        return await self.__session__.scalar(
            insert(Contact)
            .values(
                first_name=contact.first_name,
                last_name=contact.last_name,
                phone_number=contact.phone_number,
                resume_url=contact.resume_url,
                email=contact.email
            ).returning(Contact)
        )

    async def get(self, contact_id: int) -> Contact | None:
        return await self.__session__.get(Contact, contact_id)

    async def update(self, updated: Contact) -> Contact:
        contact = await self.__session__.scalar(
            update(Contact)
            .filter(updated.id == Contact.id)
            .values(
                first_name=updated.first_name,
                last_name=updated.last_name,
                phone_number=updated.phone_number,
                resume_url=updated.resume_url,
                email=updated.email
            )
            .returning(Contact)
        )

        return contact

    async def delete(self, contact_id: int) -> None:
        raise RuntimeError("Deleting contacts is prohibited")
