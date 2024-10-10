import requests
from datetime import datetime
from typing import Annotated, Dict
from fastapi import APIRouter, Request, Depends, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from requests_oauthlib import OAuth2Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config
from ..security import get_user
from app.db.database import session_factory
from app.db.models import OAuth2 as OAuth2Model
from app.db.repositories.oauth2 import OAuth2Repository, ClientHostname

router = APIRouter(prefix='/headhunter', tags=['headhunter'], dependencies=[Depends(get_user)])
DatabaseSession = Annotated[AsyncSession, Depends(session_factory)]


@router.get('/')
async def get(db: DatabaseSession):
    client = await OAuth2Repository(db).get(ClientHostname.HEADHUNTER)

    if client is None:
        raise HTTPException(status_code=404, detail='Client credential not found')

    request = requests.get('https://api.hh.ru/me', headers={
        'Authorization': f'Bearer {client.access_token}',
        'User-Agent': config.hh_application_name
    })

    return request.json()


@router.get('/auth')
async def auth(db: DatabaseSession, code: Annotated[str, Query()] = None, state: Annotated[str, Query()] = None):
    client = await OAuth2Repository(db).get(ClientHostname.HEADHUNTER)

    if client and (client.issued_at.timestamp() + client.expires_in) > datetime.now().timestamp():
        return client

    headhunter = OAuth2Session(config.hh_client_id, state=state)
    authorization_url, state = headhunter.authorization_url('https://hh.ru/oauth/authorize')

    if code is None:
        return RedirectResponse(authorization_url, status_code=status.HTTP_303_SEE_OTHER)

    token = headhunter.fetch_token(
        'https://api.hh.ru/token',
        include_client_id=True,
        client_secret=config.hh_client_secret.get_secret_value(),
        code=code,
        state=state,
        headers={
            'User-Agent': config.hh_application_name
        }
    )

    client = await OAuth2Repository(db).create(OAuth2Model(
        hostname=ClientHostname.HEADHUNTER,
        access_token=token.get('access_token'),
        refresh_token=token.get('refresh_token'),
        expires_in=token.get('expires_in')
    ))

    return client
