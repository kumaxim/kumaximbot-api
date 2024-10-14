from typing import Callable, Awaitable, Dict, Any
from contextlib import asynccontextmanager
from aiogram import Bot
from aiogram.types import BotCommand, Update
from app.db.repositories.post import PostRepository
from app.db.database import session_factory

async_session = asynccontextmanager(session_factory)


async def setup_database_session(
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
):
    async with async_session() as db:
        data['db'] = db

    return await handler(event, data)


async def setup_bot_commands(bot: Bot):
    async with async_session() as db:
        posts = await PostRepository(db).filter_by(callback_query=None)

        await bot.set_my_commands([
            BotCommand(command=post.command, description=post.title) for post in posts if post.command != 'start'
        ])

    # await bot.set_my_commands([
    #     BotCommand(command='about', description='Обо мне'),
    #     BotCommand(command='skills', description='Навыки'),
    #     BotCommand(command='experience', description='Опыт работы'),
    #     BotCommand(command='projects', description='Реализованные проекты'),
    #     BotCommand(command='education', description='Образование'),
    #     BotCommand(command='expectations', description='Ожидания от работодателя'),
    #     BotCommand(command='schedule', description='Назначить интервью'),
    #     BotCommand(command='resume', description='Скачать резюме'),
    #     BotCommand(command='contacts', description='Связаться со мной')
    # ])