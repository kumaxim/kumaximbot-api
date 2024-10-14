from os import listdir, path
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.config import config

router = APIRouter()


@router.get('/', operation_id='getHelloMessage')
async def root():
    return {
        "message": "Hello. Im am @kumaximbot API",
        "url": "https://t.me/kumaximbot"
    }


@router.get('/assets', operation_id='listServerAssets')
async def assets() -> list[str]:
    folder = config.assets_path
    documents = [filename for filename in listdir(folder) if path.isfile(path.join(folder, filename))]

    return [name for name in documents if name.endswith('.pdf')]


@router.get('/robots.txt', operation_id='getRobotsTxtFile', response_class=PlainTextResponse)
async def robots():
    return '\n'.join(['User-agent: *', 'Disallow: /'])
