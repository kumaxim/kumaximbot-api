from typing import List, Optional
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


class Phone(BaseModel):
    id: int
    number: str


class User(BaseModel):
    id: str
    login: str
    client_id: str
    display_name: str
    real_name: str
    first_name: str
    last_name: str
    sex: str
    default_email: str
    emails: List[str]
    default_phone: Phone
    psuid: str
