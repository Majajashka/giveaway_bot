
from dishka import Provider, Scope, from_context, provide

from template.config import (
    Config,
    LocalizationConfig,
    PostgresqlConfig,
    RedisConfig,
    TelegramBotConfig,
)


class ConfigProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=Config)

    @provide
    def telegram_bot(self, config: Config) -> TelegramBotConfig:
        return config.telegram_bot

    @provide
    def postgresql(self, config: Config) -> PostgresqlConfig:
        return config.postgresql

    @provide
    def localization(self, config: Config) -> LocalizationConfig:
        return config.localization

    @provide
    def redis(self, config: Config) -> RedisConfig:
        return config.redis
