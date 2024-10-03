import logging
from contextlib import asynccontextmanager

from typing import Annotated, Dict, Any
from aiogram import Bot, Dispatcher
from aiogram.types import Message, Update

from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .config import config
from .api.routers import posts, default
from .tgbot.bot import startup, dp as dispatcher, bot as current_bot


logging.getLogger().setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()

    yield

app = FastAPI(lifespan=lifespan, debug=config.dev_mode)
app.add_middleware(
    CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)
app.include_router(posts.router, prefix="/posts", tags=['posts'])
app.include_router(default.router)


@app.get('/set-webhook', tags=['tg'])
async def set_webhook(bot: Annotated[Bot, Depends(lambda: current_bot)], request: Request):
    return await bot.set_webhook(f'{request.base_url}/webhook', drop_pending_updates=True)


@app.get('/webhook-info', tags=['tg'])
async def info_webhook(bot: Annotated[Bot, Depends(lambda: current_bot)]):
    return await bot.get_webhook_info()


@app.post('/webhook', tags=['tg'])
async def webhook(update: Dict[str, Any],
                  bot: Annotated[Bot, Depends(lambda: current_bot)],
                  dp: Annotated[Dispatcher, Depends(lambda: dispatcher)],
                  response: Response):
    try:
        await dp.feed_webhook_update(bot, Update(**update))
    except:
        response.status_code = status.HTTP_200_OK


handler = Mangum(app)
