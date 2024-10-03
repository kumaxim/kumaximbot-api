from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Update, Message
from aiogram.client.default import DefaultBotProperties

from sulguk import AiogramSulgukMiddleware, SULGUK_PARSE_MODE

from app.config import config
from app.db import database
from .commands import router
from .middleware import DatabaseSessionMiddleware


bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=SULGUK_PARSE_MODE))
dp = Dispatcher()


async def startup():
    bot.session.middleware(AiogramSulgukMiddleware())

    session = database.session_factory()

    dp.update.middleware(DatabaseSessionMiddleware(await anext(session)))
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
