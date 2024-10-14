import requests
from fastapi import HTTPException, Request, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, APIKeyHeader, utils
from typing import Optional, Annotated

from app.config import config
from .schemas import User


class OAuth2AuthorizationCodeYandex(OAuth2AuthorizationCodeBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")

        if not authorization:
            authorization = request.headers.get("X-YID-Authorization")

        scheme, param = utils.get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None  # pragma: nocover

        return param


oauth2_scheme = OAuth2AuthorizationCodeYandex(
    authorizationUrl='https://oauth.yandex.ru/authorize',
    tokenUrl='https://oauth.yandex.ru/token',
    scheme_name='YandexID',
    scopes={},
)


async def get_user(access_token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing access token')

    try:
        response = requests.get('https://login.yandex.ru/info', headers={
            'Authorization': f'Bearer {access_token}',
        })

        response.raise_for_status()
    except requests.HTTPError as err:
        raise HTTPException(status_code=err.response.status_code, detail=err.response.reason)

    user = User(**response.json())

    if user.login.lower() != config.privileged_user_login:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied. Insufficient permission')

    return user


apikey_scheme = APIKeyHeader(name='X-Telegram-Bot-Api-Secret-Token')


async def get_bot_secret_token(secret_token: Annotated[str, Depends(apikey_scheme)]) -> str:
    if not secret_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Missing secret token')

    if secret_token != config.telegram_secret_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid secret token')

    return secret_token
