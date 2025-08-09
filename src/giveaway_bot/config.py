import os
import tomllib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final

from adaptix import Retort
from sqlalchemy import URL

from giveaway_bot.entities.enum.language import Language

retort: Final[Retort] = Retort()


class TelegramBotStorageType(Enum):
    REDIS = "redis"
    MEMORY = "memory"


@dataclass(slots=True, frozen=True)
class TelegramBotStorageConfig:
    storage_type: TelegramBotStorageType = TelegramBotStorageType.MEMORY
    events_isolation_type: TelegramBotStorageType = TelegramBotStorageType.MEMORY


@dataclass(slots=True, frozen=True)
class TelegramBotOwnerConfig:
    tg_user_id: int
    tg_chat_id: int
    timezone: str


@dataclass(slots=True, frozen=True)
class TelegramBotRequiredChannels:
    channels: list[int]


@dataclass(slots=True, frozen=True)
class TelegramBotConfig:
    token: str = field(repr=False)
    skip_updates: bool
    owner: TelegramBotOwnerConfig
    storage: TelegramBotStorageConfig
    required_channels: TelegramBotRequiredChannels


@dataclass(slots=True, frozen=True)
class RedisConfig:
    REDIS_HOST: str
    REDIS_PORT: int = 6379


@dataclass(slots=True, frozen=True)
class PostgresqlConfig:
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    pool_size: int = -1

    @staticmethod
    def _form_drivername(dialect: str, driver: str) -> str:
        if all((driver, dialect)):
            drivername = f"{dialect}+{driver}"
        else:
            drivername = dialect
        return drivername

    def get_database_url(self, dialect: str = "postgresql", driver: str = "psycopg") -> URL:
        url = URL.create(
            drivername=self._form_drivername(dialect, driver),
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )
        return url


@dataclass(frozen=True, slots=True)
class LocalizationConfig:
    path: Path
    default_language: Language


@dataclass(frozen=True, slots=True)
class IntegrationConfig:
    service_url: str


@dataclass(frozen=True, slots=True)
class Config:
    telegram_bot: TelegramBotConfig
    localization: LocalizationConfig
    postgresql: PostgresqlConfig
    redis: RedisConfig
    integration: IntegrationConfig


def _load_postgresql_secrets() -> dict[str, str]:
    return {
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB"),
        "POSTGRES_PORT": int(os.getenv("POSTGRES_PORT")),
    }


def _load_redis_secrets() -> dict[str, str]:
    return {
        "REDIS_HOST": os.getenv("REDIS_HOST"),
        "REDIS_PORT": int(os.getenv("REDIS_PORT")),
    }


def build_config(path: Path) -> Config:
    with open(path, "rb") as file:
        raw_data = tomllib.load(file)
        raw_data["postgresql"].update(_load_postgresql_secrets())
        raw_data["redis"] = (_load_redis_secrets())
    return retort.load(raw_data, Config)
