import requests
from pydantic import create_model
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import OAuth2Error

from app.config import config

from ..security import get_user
from ..schemas import User, OAuth2Token, OAuth2TokenRevoke

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', operation_id='getUserInfo')
async def info(user: Annotated[User, Depends(get_user)]) -> User:
    return user


@router.get('/login/redirect',
            operation_id='redirectToAuthorize',
            response_class=RedirectResponse,
            status_code=status.HTTP_303_SEE_OTHER)
async def redirect() -> RedirectResponse:
    oauth = OAuth2Session(config.yandex_oauth_client_id)
    authorization_url, state = oauth.authorization_url('https://oauth.yandex.ru/authorize', device_id='kumaximbot')

    return RedirectResponse(authorization_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post('/login', operation_id='getOAuthToken')
async def login(body: create_model('LoginBody', code=(str, ...), state=(str, ...))) -> OAuth2Token:
    oauth = OAuth2Session(config.yandex_oauth_client_id, state=body.state)

    try:
        token = oauth.fetch_token(
            'https://oauth.yandex.ru/token',
            include_client_id=True,
            client_secret=config.yandex_oauth_client_secret.get_secret_value(),
            code=body.code,
            state=body.state,
        )
    except OAuth2Error as err:
        raise HTTPException(status_code=err.status_code, detail=err.description)

    return OAuth2Token(
        access_token=token.get('access_token'),
        token_type=token.get('token_type'),
        refresh_token=token.get('refresh_token'),
        expires_in=token.get('expires_in'),
        scope=token.get('scope')
    )


@router.post('/refresh', operation_id='refreshOAuthToken')
async def refresh(body: create_model('RefreshBody', refresh_token=(str, ...))) -> OAuth2Token:
    oauth = OAuth2Session(config.yandex_oauth_client_id)
    token = oauth.refresh_token(
        'https://oauth.yandex.ru/token',
        client_secret=config.yandex_oauth_client_secret.get_secret_value(),
        refresh_token=body.refresh_token
    )

    return OAuth2Token(**token)


@router.post('/logout', operation_id='removeOAuth2Token', dependencies=[Depends(get_user)])
async def logout(body: create_model('LogoutBody', access_token=(str, ...))) -> OAuth2TokenRevoke:
    try:
        response = requests.post('https://oauth.yandex.ru/revoke_token', data={
            'access_token': body.access_token,
            'client_id': config.yandex_oauth_client_id,
            'client_secret': config.yandex_oauth_client_secret.get_secret_value()
        })

        response.raise_for_status()
    except requests.HTTPError as err:
        raise HTTPException(status_code=err.response.status_code, detail=err.response.json())

    return OAuth2TokenRevoke(**response.json())
