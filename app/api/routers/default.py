from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get('/')
async def root():
    return {
        "hello": "Im am @kumaximbot API",
        "url": "https://t.me/kumaximbot"
    }


@router.get('/robots.txt', response_class=PlainTextResponse)
async def robots():
    return '\n'.join(['User-agent: *', 'Disallow: /'])
