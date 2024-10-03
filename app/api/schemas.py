from pydantic import BaseModel
from typing import Annotated, Any, Optional, Dict


class Post(BaseModel):
    id: int
    command: str
    text: str


class CreatePost(BaseModel):
    command: str
    text: str


class UpdatePost(CreatePost):
    pass
