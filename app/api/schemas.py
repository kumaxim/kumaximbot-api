from typing import Optional
from pydantic import BaseModel


class Post(BaseModel):
    id: int
    command: str
    callback_query: Optional[str] = None
    title: str
    text: str


class CreatePost(BaseModel):
    command: str
    callback_query: Optional[str] = None
    title: str
    text: str


class UpdatePost(CreatePost):
    pass


class Contact(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone_number: str
    resume_url: str
    email: str


class CreateContact(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    resume_url: str
    email: str


class UpdateContact(CreateContact):
    pass
