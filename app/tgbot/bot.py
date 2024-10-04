import logging
from sys import stdout as sys_stdout
from asyncio import run as async_run
from contextlib import asynccontextmanager
from typing import Callable, Awaitable, Dict, Any

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Update
from aiogram.client.default import DefaultBotProperties
from sulguk import AiogramSulgukMiddleware, SULGUK_PARSE_MODE

from app.config import config
from app.db.database import session_factory
from .commands import router


bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=SULGUK_PARSE_MODE))
dp = Dispatcher()


async def setup_database_session(
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
):
    database_session = asynccontextmanager(session_factory)

    async with database_session() as session:
        data['db'] = session

        return await handler(event, data)


async def on_startup():
    bot.session.middleware(AiogramSulgukMiddleware())
    dp.update.outer_middleware(setup_database_session)
    dp.include_router(router)

    await bot.set_my_commands([
        BotCommand(command='about', description='Обо мне'),
        BotCommand(command='skills', description='Навыки'),
        BotCommand(command='experience', description='Опыт работы'),
        BotCommand(command='projects', description='Реализованные проекты'),
        BotCommand(command='education', description='Образование'),
        BotCommand(command='expectations', description='Ожидания от работодателя'),
        BotCommand(command='schedule', description='Назначить интервью'),
        BotCommand(command='resume', description='Скачать резюме'),
        BotCommand(command='contacts', description='Связаться со мной')
    ])
