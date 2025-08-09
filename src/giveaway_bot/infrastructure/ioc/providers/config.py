
from dishka import Provider, Scope, from_context, provide

from giveaway_bot.config import (
    Config,
    LocalizationConfig,
    PostgresqlConfig,
    RedisConfig,
    TelegramBotConfig, TelegramBotOwnerConfig, TelegramBotRequiredChannels, IntegrationConfig,
)


class ConfigProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=Config)

    @provide
    def telegram_bot(self, config: Config) -> TelegramBotConfig:
        return config.telegram_bot

    @provide
    def owner_config(self, config: Config) -> TelegramBotOwnerConfig:
        return config.telegram_bot.owner

    @provide
    def telegram_required_channels(self, config: TelegramBotConfig) -> TelegramBotRequiredChannels:
        return config.required_channels

    @provide
    def postgresql(self, config: Config) -> PostgresqlConfig:
        return config.postgresql

    @provide
    def localization(self, config: Config) -> LocalizationConfig:
        return config.localization

    @provide
    def redis(self, config: Config) -> RedisConfig:
        return config.redis

    @provide
    def integration_config(self, config: Config) -> IntegrationConfig:
        return config.integration
