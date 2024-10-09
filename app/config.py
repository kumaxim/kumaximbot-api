from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    telegram_secret_token: SecretStr
    sqlite_path: str = '/assets/db.sqlite'
    dev_mode: bool = False

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()

