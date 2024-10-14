from typing import Annotated, Dict, Any
from aiogram import Bot, Dispatcher
from aiogram.types import Update, WebhookInfo
from aiogram.exceptions import AiogramError
from fastapi import APIRouter, Request, Response, status, Depends
from app.tgbot.bot import dp as dispatcher, bot as current_bot
from app.logger import logger
from ..security import get_bot_secret_token, get_user

router = APIRouter(prefix='/telegram', tags=['telegram'])


@router.get('/set-webhook', status_code=204)
async def set_webhook(bot: Annotated[Bot, Depends(lambda: current_bot)],
                      request: Request,
                      secret_token: Annotated[str, Depends(get_bot_secret_token)]) -> None:
    await bot.set_webhook(
        f'{request.base_url}/{router.prefix}/webhook',
        secret_token=secret_token,
        drop_pending_updates=True
    )


@router.get('/webhook-info', dependencies=[Depends(get_user)])
async def info_webhook(bot: Annotated[Bot, Depends(lambda: current_bot)]) -> WebhookInfo:
    return await bot.get_webhook_info()


@router.post('/webhook', dependencies=[Depends(get_bot_secret_token)])
async def webhook(update: Dict[str, Any],
                  bot: Annotated[Bot, Depends(lambda: current_bot)],
                  dp: Annotated[Dispatcher, Depends(lambda: dispatcher)],
                  response: Response) -> None:
    try:
        return await dp.feed_webhook_update(bot, Update(**update))
    except AiogramError as error:
        logger.error(error)

        response.status_code = status.HTTP_200_OK
