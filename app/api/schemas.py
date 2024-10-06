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
