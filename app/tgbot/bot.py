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
from app.db.database import scoped_session, session_factory
from app.db.repositories.post import PostRepository
from .storage import SQLAlchemyStorage
from .handlers import router

bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=SULGUK_PARSE_MODE))
dp = Dispatcher(storage=SQLAlchemyStorage(scoped_session))


async def setup_database_session(
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
):
    async with asynccontextmanager(session_factory)() as session:
        data['db'] = session

        return await handler(event, data)


async def on_startup():
    bot.session.middleware(AiogramSulgukMiddleware())
    dp.update.outer_middleware(setup_database_session)
    dp.include_router(router)

    session_manager = asynccontextmanager(session_factory)

    async with session_manager() as session:
        posts = await PostRepository(session).filter_by(callback_query=None)

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


async def local_runner():
    """
    Start the bot in long polling mode for local development.

    If bot's webhook is set, it will be destroyed before starting polling.
    """
    info = await bot.get_webhook_info()

    if info.url:
        await bot.delete_webhook(drop_pending_updates=True)

    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys_stdout)
    async_run(local_runner())
