from typing import Annotated, Dict, Any
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from fastapi import APIRouter, Request, Response, status, Depends, Header

from app.tgbot.bot import on_startup, dp as dispatcher, bot as current_bot
from app.config import config

router = APIRouter(prefix='/tg', tags=['telegram'])


@router.get('/set-webhook')
async def set_webhook(bot: Annotated[Bot, Depends(lambda: current_bot)], request: Request) -> None:
    await bot.set_webhook(f'{request.base_url}/{router.prefix}/webhook',
                          secret_token=config.telegram_secret_token,
                          drop_pending_updates=True
                          )


@router.get('/webhook-info')
async def info_webhook(bot: Annotated[Bot, Depends(lambda: current_bot)]):
    return await bot.get_webhook_info()


@router.post('/webhook')
async def webhook(update: Dict[str, Any],
                  bot: Annotated[Bot, Depends(lambda: current_bot)],
                  dp: Annotated[Dispatcher, Depends(lambda: dispatcher)],
                  response: Response,
                  secret_token: Annotated[str | None, Header(..., alias='X-Telegram-Bot-Api-Secret-Token')] = None):
    if secret_token != config.telegram_secret_token:
        response.status_code = status.HTTP_403_FORBIDDEN

        return
    try:
        await on_startup()
        await dp.feed_webhook_update(bot, Update(**update))
    except Exception as ex:
        response.status_code = status.HTTP_200_OK
