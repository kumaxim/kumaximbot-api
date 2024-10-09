from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import session_factory
from app.db.models import Contact as ContactModel
from app.db.repositories.contact import ContactRepository
from ..schemas import Contact, CreateContact, UpdateContact

router = APIRouter(prefix='/contacts', tags=['contacts'])
DatabaseSession = Annotated[AsyncSession, Depends(session_factory)]


@router.get('/', operation_id='listContacts')
async def get_contacts(db: DatabaseSession) -> Sequence[Contact]:
    return await ContactRepository(db).get_all()


@router.post('/', operation_id='createContact')
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


@router.put('/{contact_id}', operation_id='updateContact')
async def update_contact(contact_id: int, contact: UpdateContact, db: DatabaseSession) -> Contact:
    return await ContactRepository(db).update(
        ContactModel(id=contact_id, **contact.__dict__)
    )
