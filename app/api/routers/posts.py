from typing import Annotated, Sequence
from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import session_factory
from app.db.models import Post as PostModel
from app.db.repositories.post import PostRepository

from ..schemas import Post, CreatePost, UpdatePost


router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(session_factory)] 


@router.get("/", operation_id='listPosts')
async def get_posts(session: Annotated[AsyncSession, Depends(session_factory)]) -> Sequence[Post]:
    all_posts = await PostRepository(session).get_all()

    return all_posts


@router.get('/{post_id}', operation_id='getPost',  responses={404: {}})
async def get_post(post_id: int, session: DatabaseSession) -> Post:
    post = await PostRepository(session).get(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.post("/", operation_id='createPost', responses={409: {}})
async def create_post(post: CreatePost, session: DatabaseSession) -> Post:
    try:
        return await PostRepository(session).create(
            PostModel(text=post.text, title=post.title, command=post.command, callback_query=post.callback_query)
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail=f"Post with command '{post.command}' already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail='Unknown error')


@router.put("/{post_id}", operation_id='replacePost')
async def update_post(post_id: int, post: UpdatePost, session: DatabaseSession) -> Post:
    return await PostRepository(session).update(
        PostModel(id=post_id, title=post.title, text=post.text, command=post.command, callback_query=post.callback_query)
    )


@router.delete("/{post_id}", operation_id='deletePost', status_code=204)
async def delete_post(post_id: int, session: DatabaseSession) -> None:
    await PostRepository(session).delete(post_id)
