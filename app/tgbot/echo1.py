from contextlib import asynccontextmanager

from aiogram import Dispatcher
from aiogram.types import Message

dp = Dispatcher()


@asynccontextmanager
async def setup_dispatcher():
    yield dp


@dp.message()
async def echo(message: Message):
    await message.send_copy(message.chat.id)
