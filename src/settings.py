from typing import TypeVar

import dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

TSettings = TypeVar("TSettings", bound=BaseSettings)


def get_settings(cls: type[TSettings]) -> TSettings:
    dotenv.load_dotenv()
    return cls()


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True, env_prefix="mongo_")

    uri_local: str
    uri: str


class TelegramBotSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True, env_prefix="bot_")

    token: SecretStr
