from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    telegram_secret_token: SecretStr
    sqlite_path: str = '/assets/db.sqlite'
    dev_mode: bool = False
    hh_client_id: str
    hh_client_secret: SecretStr
    hh_application_name: str
    hh_resume_id: str
    yandex_oauth_client_id: str
    yandex_oauth_client_secret: SecretStr
    privileged_user_login: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()

