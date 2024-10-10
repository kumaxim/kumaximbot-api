from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import session_factory
from app.db.models import Contact as ContactModel
from app.db.repositories.contact import ContactRepository
from ..security import get_user
from ..schemas import Contact, CreateContact, UpdateContact

router = APIRouter(prefix='/contacts', tags=['contacts'])
protected = APIRouter(dependencies=[Depends(get_user)])
DatabaseSession = Annotated[AsyncSession, Depends(session_factory)]


@router.get('/', operation_id='listContacts')
async def get_contacts(db: DatabaseSession) -> Sequence[Contact]:
    return await ContactRepository(db).get_all()


@protected.post('/', operation_id='createContact')
async def create_contact(contact: CreateContact, db: DatabaseSession) -> Contact:
    return await ContactRepository(db).create(
        ContactModel(**contact.__dict__)
    )


@router.get('/{contact_id}', operation_id='getContact')
async def get_contact(contact_id: int, db: DatabaseSession) -> Contact:
    contact = await ContactRepository(db).get(contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail='Contact not found')

    return contact


@protected.put('/{contact_id}', operation_id='updateContact')
async def update_contact(contact_id: int, contact: UpdateContact, db: DatabaseSession) -> Contact:
    return await ContactRepository(db).update(
        ContactModel(id=contact_id, **contact.__dict__)
    )


@protected.delete('/{contact_id}', operation_id='deleteContact', status_code=204)
async def delete_contact(contact_id: int, db: DatabaseSession) -> None:
    await ContactRepository(db).delete(contact_id)
