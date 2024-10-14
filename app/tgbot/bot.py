from asyncio import run as async_run
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from sulguk import AiogramSulgukMiddleware, SULGUK_PARSE_MODE
from app.config import config
from app.db.database import scoped_session
from .storage import SQLAlchemyStorage
from .startup import setup_bot_commands, setup_database_session
from .handlers import router

bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=SULGUK_PARSE_MODE))
bot.session.middleware(AiogramSulgukMiddleware())

dp = Dispatcher(storage=SQLAlchemyStorage(scoped_session))
dp.update.outer_middleware(setup_database_session)
dp.startup.register(setup_bot_commands)
dp.include_router(router)


async def local_runner():
    """
    Start the bot in long polling mode for local development.

    If bot's webhook is set, it will be destroyed before starting polling.
    """
    info = await bot.get_webhook_info()

    if info.url:
        await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == '__main__':
    async_run(local_runner())
